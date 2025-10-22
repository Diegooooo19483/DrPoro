# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, crud, schemas
from typing import List
import io
import csv
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dr. Poro - API de Estadísticas de LoL")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Champions CRUD ---
@app.post("/campeones", response_model=schemas.Champion, status_code=status.HTTP_201_CREATED)
def create_champion(champion: schemas.ChampionCreate, db: Session = Depends(get_db)):
    existing = crud.get_champion_by_name(db, champion.nombre)
    if existing:
        raise HTTPException(status_code=400, detail="Campeón ya existe")
    return crud.create_champion(db, champion)

@app.get("/campeones", response_model=List[schemas.Champion])
def list_champions(skip: int = 0, limit: int = 100, include_inactive: bool = False, db: Session = Depends(get_db)):
    return crud.list_champions(db, skip, limit, include_inactive)

@app.get("/campeones/{champion_id}", response_model=schemas.Champion)
def get_champion(champion_id: int, db: Session = Depends(get_db)):
    db_champ = crud.get_champion(db, champion_id)
    if not db_champ:
        raise HTTPException(status_code=404, detail="Campeón no encontrado")
    return db_champ

@app.put("/campeones/{champion_id}", response_model=schemas.Champion)
def put_champion(champion_id: int, champ_update: schemas.ChampionCreate, db: Session = Depends(get_db)):
    db_champ = crud.get_champion(db, champion_id)
    if not db_champ:
        raise HTTPException(status_code=404, detail="Campeón no encontrado")
    # overwrite fields
    db_champ.nombre = champ_update.nombre
    db_champ.rol = champ_update.rol
    db_champ.tasa_victoria = champ_update.tasa_victoria
    db_champ.tasa_seleccion = champ_update.tasa_seleccion
    db_champ.tasa_baneo = champ_update.tasa_baneo
    if champ_update.profile:
        if db_champ.profile:
            db_champ.profile.descripcion = champ_update.profile.descripcion
            db_champ.profile.historia = champ_update.profile.historia
        else:
            db_champ.profile = models.Profile(descripcion=champ_update.profile.descripcion, historia=champ_update.profile.historia)
    db.add(db_champ)
    db.commit()
    db.refresh(db_champ)
    return db_champ

@app.patch("/campeones/{champion_id}", response_model=schemas.Champion)
def patch_champion(champion_id: int, champ_update: schemas.ChampionUpdate, db: Session = Depends(get_db)):
    db_champ = crud.get_champion(db, champion_id)
    if not db_champ:
        raise HTTPException(status_code=404, detail="Campeón no encontrado")
    updated = crud.update_champion(db, champion_id, champ_update)
    if not updated:
        raise HTTPException(status_code=400, detail="No se pudo actualizar")
    return updated

@app.delete("/campeones/{champion_id}", response_model=schemas.Champion)
def delete_champion(champion_id: int, db: Session = Depends(get_db)):
    db_champ = crud.soft_delete_champion(db, champion_id)
    if not db_champ:
        raise HTTPException(status_code=404, detail="Campeón no encontrado")
    return db_champ

# --- Items CRUD ---
@app.post("/objetos", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)

@app.get("/objetos", response_model=List[schemas.Item])
def list_items(skip: int=0, limit:int=100, include_inactive: bool=False, db: Session=Depends(get_db)):
    return crud.list_items(db, skip, limit, include_inactive)

@app.get("/objetos/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session=Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Objeto no encontrado")
    return db_item

@app.delete("/objetos/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session=Depends(get_db)):
    db_item = crud.soft_delete_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Objeto no encontrado")
    return db_item

# --- Asociaciones: items <-> champions ---
@app.post("/campeones/{champion_id}/objetos/{item_id}")
def add_item_to_champion(champion_id: int, item_id: int, porcentaje_uso: float = 0.0, db: Session = Depends(get_db)):
    champ = crud.get_champion(db, champion_id)
    item = crud.get_item(db, item_id)
    if not champ or not item:
        raise HTTPException(status_code=404, detail="Campeón u objeto no encontrado")
    assoc = crud.add_item_to_champion(db, champion_id, item_id, porcentaje_uso)
    return {"message": "Asociado", "association_id": assoc.id}

@app.get("/campeones/{champion_id}/objetos", response_model=List[schemas.Item])
def get_items_for_champion(champion_id: int, db: Session = Depends(get_db)):
    champ = crud.get_champion(db, champion_id)
    if not champ:
        raise HTTPException(status_code=404, detail="Campeón no encontrado")
    return crud.get_items_for_champion(db, champion_id)

# --- Champion vs Champion ---
@app.post("/cvc", response_model=schemas.CVC, status_code=status.HTTP_201_CREATED)
def create_cvc(cvc: schemas.CVCCreate, db: Session = Depends(get_db)):
    # validate champions exist
    if not crud.get_champion(db, cvc.champion_id) or not crud.get_champion(db, cvc.oponente_id):
        raise HTTPException(status_code=404, detail="Champion oponente no encontrado")
    return crud.add_cvc(db, cvc)

@app.get("/campeones/{champion_id}/contrincantes", response_model=List[schemas.CVC])
def get_contrincantes(champion_id: int, db: Session = Depends(get_db)):
    champ = crud.get_champion(db, champion_id)
    if not champ:
        raise HTTPException(status_code=404, detail="Campeón no encontrado")
    return crud.get_cvc_by_champion(db, champion_id)

# --- Reportes ---
@app.get("/reportes/campeones")
def reporte_campeones(format: str = "csv", db: Session = Depends(get_db)):
    """Genera reporte de campeones en format csv/xlsx/pdf"""
    champs = crud.list_champions(db, include_inactive=True)
    rows = []
    for c in champs:
        items = ", ".join([it.nombre for it in c.items])
        rows.append({
            "id": c.id,
            "nombre": c.nombre,
            "rol": c.rol,
            "tasa_victoria": c.tasa_victoria,
            "tasa_seleccion": c.tasa_seleccion,
            "tasa_baneo": c.tasa_baneo,
            "activo": c.activo,
            "objetos": items
        })
    df = pd.DataFrame(rows)

    if format == "csv":
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        return Response(content=stream.getvalue(), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=report_campeones.csv"})
    elif format == "xlsx":
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="campeones")
            writer.save()
        out.seek(0)
        return Response(content=out.read(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition":"attachment; filename=report_campeones.xlsx"})
    elif format == "pdf":
        out = io.BytesIO()
        doc = SimpleDocTemplate(out, pagesize=letter)
        style = getSampleStyleSheet()
        data = [list(df.columns)]
        for _, row in df.iterrows():
            data.append([str(x) for x in row.tolist()])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING',(0,0),(-1,0),12),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black)
        ]))
        elems = [Paragraph("Reporte de Campeones", style['Heading2']), table]
        doc.build(elems)
        out.seek(0)
        return Response(content=out.read(), media_type="application/pdf", headers={"Content-Disposition":"attachment; filename=report_campeones.pdf"})
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado. Use csv|xlsx|pdf")
