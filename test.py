from database import engine, Session

with Session(engine) as session:
    try:
        result = session.exec("SELECT NOW()").first()
        print("Conexión exitosa! Hora de DB:", result)
    except Exception as e:
        print("Error al conectar:", e)
