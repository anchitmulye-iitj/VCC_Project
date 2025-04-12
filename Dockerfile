# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (if you need them)
RUN apt-get update && apt-get install -y gcc

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy your application code
COPY requirements.txt .
COPY ml_api.py .
COPY inference.py .
COPY detect_trend.py .
COPY scaler.save .
COPY lstm_model.h5 .

# Expose port
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "ml_api:app", "--host", "0.0.0.0", "--port", "8000"]
