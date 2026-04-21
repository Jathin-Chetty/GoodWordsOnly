FROM python:3.10-slim

# Set up a non-root user with user ID 1000
RUN useradd -m -u 1000 user

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=user:user . .

# Switch to the non-root user
USER user

# Hugging Face Spaces require port 7860
EXPOSE 7860

# Command to run the application using gunicorn
CMD ["gunicorn", "webapp.app:app", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120"]
