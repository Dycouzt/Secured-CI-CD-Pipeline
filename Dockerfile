# Stage 1: The Builder
# Using a more recent version of Python and a newer OS (Bullseye) to inherit fewer vulnerabilities.
FROM python:3.11-slim-bullseye as builder

# Secure: Update OS packages and apply security patches BEFORE adding application code.
# This reduces the attack surface from the very beginning.
# The `-y` flag auto-confirms, and `rm -rf` cleans up the apt cache to keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends gcc && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN pip install --upgrade pip

# Copy requirements and install dependencies
COPY ./app/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Final Stage ---
FROM python:3.11-slim-bullseye

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