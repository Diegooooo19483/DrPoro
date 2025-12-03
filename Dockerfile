FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV DATABASE_URL="sqlite:///./drporo.db"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
