# Gurujix service-orders — container image
# Platform lesson: same app runs on laptop and later in Kubernetes via an image.
FROM python:3.13-slim

WORKDIR /app

# Install dependencies first (better layer caching when only app code changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app ./app

# Non-root user (good default for Kubernetes later)
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Bind 0.0.0.0 so the port is reachable from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
