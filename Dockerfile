# Dockerfile

# --- Build Stage ---
# Use a specific version for reproducibility.
FROM python:3.9-slim-buster AS builder

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN pip install --upgrade pip

# Copy requirements and install dependencies
COPY ./app/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Final Stage ---
FROM python:3.9-slim-buster

# Create a non-root user for security
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Copy built wheels and application code from the builder stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
COPY ./app .

# Install dependencies from local wheels to avoid hitting the network
# This also ensures we use the exact packages from the build stage
RUN pip install --no-cache /wheels/*

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /home/appuser

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application using a production-grade server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]