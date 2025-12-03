from fastapi import APIRouter, Form, File, UploadFile, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from typing import List

import database, crud, models, schemas
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/userprofiles", tags=["UserProfiles"])

# -----------------------------
# DB SESSION
# -----------------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# FORMULARIO NUEVO PERFIL
# -----------------------------
@router.get("/new")
def new_userprofile_form(request: Request, db: Session = Depends(get_db)):
    all_champions = db.query(models.Champion).all()
    return templates.TemplateResponse(
        "profile/userprofile_create.html",
        {"request": request, "all_champions": all_champions}
    )


# -----------------------------
# CREAR NUEVO PERFIL (POST)
# -----------------------------
@router.post("/new")
def submit_new_userprofile(
    request: Request,
    nombre_perfil: str = Form(...),
    nombre_cuenta: str = Form(...),
    region: str = Form(None),
    campeones_favoritos_ids: List[int] = Form([]),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    filename = None
    if foto:
        os.makedirs("static/uploads", exist_ok=True)
        filename = f"static/uploads/{foto.filename}"
        with open(filename, "wb") as f:
            f.write(foto.file.read())

    # Crear el perfil en la DB
    profile_data = schemas.UserProfileCreate(
        nombre_perfil=nombre_perfil,
        nombre_cuenta=nombre_cuenta,
        region=region,
        foto=filename
    )

    db_profile = crud.create_userprofile(db, profile_data)

    # Agregar campeones favoritos si se seleccionaron
    if campeones_favoritos_ids:
        champions = db.query(models.Champion).filter(
            models.Champion.id.in_(campeones_favoritos_ids)
        ).all()
        db_profile.campeones_favoritos = champions
        db.commit()
        db.refresh(db_profile)

    # Redirigir a la vista del perfil creado
    return RedirectResponse(url=f"/userprofiles/view/{db_profile.id}", status_code=302)


# -----------------------------
# VER PERFIL
# -----------------------------
@router.get("/view/{profile_id}")
def view_userprofile(profile_id: int, request: Request, db: Session = Depends(get_db)):
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == profile_id).first()
    if not profile:
        return RedirectResponse("/userprofiles/new")
    return templates.TemplateResponse(
        "profile/view.html",
        {"request": request, "profile": profile}
    )
