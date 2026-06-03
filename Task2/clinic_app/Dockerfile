FROM python:3.11-slim

# The same container image is used for local Docker evidence and Render Docker deployment.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# requirements.txt is kept small so the Flask prototype builds quickly in CI and Render.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the web service as a non-root user for safer container execution.
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Render provides PORT in the cloud; local Docker falls back to port 5000.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} app:app"]
