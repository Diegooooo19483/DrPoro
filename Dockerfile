FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# No forzamos SQLite, usamos la variable de entorno en Render
ENV DATABASE_URL=${POSTGRESQL_ADDON_URI}

# Ejecutar la app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
