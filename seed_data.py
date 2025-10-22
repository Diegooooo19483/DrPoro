# seed_data.py
from database import SessionLocal, engine, Base
import models
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

champions_sample = [
    {"nombre":"Ahri","rol":"Mago","tasa_victoria":51.2,"tasa_seleccion":8.3,"tasa_baneo":2.1},
    {"nombre":"Garen","rol":"Luchador","tasa_victoria":49.7,"tasa_seleccion":12.5,"tasa_baneo":3.0},
    {"nombre":"Ezreal","rol":"Tirador","tasa_victoria":50.4,"tasa_seleccion":9.1,"tasa_baneo":1.0},
    {"nombre":"Thresh","rol":"Soporte","tasa_victoria":48.9,"tasa_seleccion":7.8,"tasa_baneo":0.5},
    {"nombre":"Zed","rol":"Asesino","tasa_victoria":52.0,"tasa_seleccion":6.2,"tasa_baneo":4.0},
]

items_sample = [
    {"nombre":"Hoja del Rey Arruinado","tipo":"Ofensivo","porcentaje_uso":12.0},
    {"nombre":"Filo Infinito","tipo":"Ofensivo","porcentaje_uso":10.5},
    {"nombre":"Cetro de Cristal de Rylai","tipo":"Mágico","porcentaje_uso":5.2},
    {"nombre":"Redención","tipo":"Soporte","porcentaje_uso":3.8},
    {"nombre":"Fuerza de la Trinidad","tipo":"Ofensivo","porcentaje_uso":7.0},
]

def seed():
    db: Session = SessionLocal()
    try:
        # limpiar
        db.query(models.ChampionItem).delete()
        db.query(models.ChampionVsChampion).delete()
        db.query(models.Profile).delete()
        db.query(models.Champion).delete()
        db.query(models.Item).delete()
        db.commit()

        champs = []
        for c in champions_sample:
            champ = models.Champion(
                nombre=c["nombre"],
                rol=c["rol"],
                tasa_victoria=c["tasa_victoria"],
                tasa_seleccion=c["tasa_seleccion"],
                tasa_baneo=c["tasa_baneo"]
            )
            champ.profile = models.Profile(descripcion=f"Perfil de {c['nombre']}", historia=f"Historia breve de {c['nombre']}")
            db.add(champ)
            champs.append(champ)
        for it in items_sample:
            item = models.Item(nombre=it["nombre"], tipo=it["tipo"], porcentaje_uso=it["porcentaje_uso"])
            db.add(item)
        db.commit()

        # asociación items - campeones
        # ejemplo: Ahri usa Cetro, Zed usa Hoja, etc.
        ahri = db.query(models.Champion).filter(models.Champion.nombre=="Ahri").first()
        zed = db.query(models.Champion).filter(models.Champion.nombre=="Zed").first()
        rylai = db.query(models.Item).filter(models.Item.nombre=="Cetro de Cristal de Rylai").first()
        hoja = db.query(models.Item).filter(models.Item.nombre=="Hoja del Rey Arruinado").first()
        filo = db.query(models.Item).filter(models.Item.nombre=="Filo Infinito").first()

        db.add(models.ChampionItem(champion_id=ahri.id, item_id=rylai.id, porcentaje_uso=8.5))
        db.add(models.ChampionItem(champion_id=zed.id, item_id=hoja.id, porcentaje_uso=15.0))
        db.add(models.ChampionItem(champion_id=champs[2].id, item_id=filo.id, porcentaje_uso=9.7))  # Ezreal -> Filo (ej)
        db.commit()

        # cvc examples
        db.add(models.ChampionVsChampion(champion_id=ahri.id, oponente_id=zed.id, winrate=46.2))
        db.add(models.ChampionVsChampion(champion_id=zed.id, oponente_id=ahri.id, winrate=53.8))
        db.commit()

        print("Seed completo.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
