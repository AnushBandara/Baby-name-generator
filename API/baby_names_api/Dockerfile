FROM python:3.10-slim

# Reduce Python buffering and TensorFlow spammy logs
ENV PYTHONUNBUFFERED=1 \
    TF_CPP_MIN_LOG_LEVEL=2

WORKDIR /app

# System dependencies (TensorFlow + NumPy + general libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (including Models folder)
COPY app ./app

# Expose the port the app will listen on
EXPOSE 8080

# Run the FastAPI app with uvicorn
# NOTE: "app.main:app" assumes your main file is app/main.py and FastAPI instance is `app`
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]