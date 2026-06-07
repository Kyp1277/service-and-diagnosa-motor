FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY database.py .
COPY diagnostic_engine.py .
COPY static/ ./static/
COPY templates/ ./templates/

# Create data directory for SQLite
RUN mkdir -p /app/data

# HuggingFace Spaces runs on port 7860
EXPOSE 7860

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "app:app"]
