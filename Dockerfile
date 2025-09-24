# --- Build Stage ---
# Use a specific version of the base image for reproducibility.
FROM python:3.11-slim-bookworm AS builder

# Set the working directory.
WORKDIR /usr/src/app

# Set environment variables to improve security and performance.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies.
RUN pip install --no-cache-dir --upgrade pip

# Copy and install application dependencies.
COPY app/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Final Stage ---
# Use a minimal, non-root base image.
FROM python:3.11-slim-bookworm

# Set the working directory.
WORKDIR /usr/src/app

# Create a non-root user and group.
# This is a critical security best practice (Principle of Least Privilege).
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Copy installed dependencies from the builder stage.
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Install dependencies from local wheels to avoid network calls.
RUN pip install --no-cache-dir /wheels/*

# Copy the application source code.
COPY ./app .

# Change ownership of the application directory to the non-root user.
RUN chown -R nonroot:nonroot /usr/src/app

# Switch to the non-root user.
USER nonroot

# Expose the port the app runs on.
EXPOSE 5000

# Define the command to run the application.
# Use gunicorn for a production-ready server instead of Flask's dev server.
# We need to install it first.
USER root
RUN pip install --no-cache-dir gunicorn
RUN chown -R nonroot:nonroot /usr/local/lib/python3.11/site-packages/
USER nonroot

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
