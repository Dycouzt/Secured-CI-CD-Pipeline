# Dockerfile - Production Hardened with Distroless

# --- Build Stage ---
FROM python:3.11-slim-bookworm AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN pip install --upgrade pip

# Copy requirements and install dependencies
COPY ./app/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Final Stage with Distroless ---
# Distroless images contain only the application and runtime dependencies
# No shell, package managers, or unnecessary OS utilities
FROM gcr.io/distroless/python3-debian12:nonroot

# Set working directory
WORKDIR /home/nonroot

# Copy wheels and install (distroless has pip)
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Copy application code
COPY --chown=nonroot:nonroot ./app .

# Install Python dependencies
RUN pip install --no-cache /wheels/*

# Distroless already runs as non-root user 'nonroot' (UID 65532)
# No need to create user or switch

# Expose the port
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]