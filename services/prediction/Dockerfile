FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/app/data
WORKDIR /app/services/prediction
COPY services/prediction/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY services/prediction .
COPY scripts /app/scripts
COPY data/config /app/data/config
COPY data/calendar /app/data/calendar
COPY data/processed /app/data/processed
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

