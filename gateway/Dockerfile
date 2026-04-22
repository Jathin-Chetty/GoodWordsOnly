FROM python:3.10-alpine

WORKDIR /app

COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy gateway app
COPY gateway/app.py .

# Copy frontend
COPY webapp/ webapp/

# Create data directory for PVC
RUN mkdir -p /app/data && chown -R nobody:nobody /app/data

# Run as non-root
USER nobody

EXPOSE 8080

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "--worker-tmp-dir", "/tmp", "--no-control-socket"]
