# Dockerfile - Alpine Base (Minimal vulnerabilities)

# --- Build Stage ---
FROM python:3.11-alpine3.19 AS builder

# Alpine uses apk instead of apt-get
# Install build dependencies needed for Python packages
RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and build wheels
COPY ./app/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Final Stage ---
FROM python:3.11-alpine3.19

# Create non-root user
RUN adduser -D appuser

WORKDIR /home/appuser

# Copy wheels and application from builder
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
COPY ./app .

# Install dependencies from wheels
RUN pip install --no-cache /wheels/*

# Set ownership
RUN chown -R appuser:appuser /home/appuser

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/health || exit 1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]