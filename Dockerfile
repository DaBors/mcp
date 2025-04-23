FROM python:3.10-slim

WORKDIR /app

# Copy lock file and code
COPY requirements.txt .
COPY main.py .

# Install dependencies using the lock file
RUN pip install -r requirements.txt

# Cloud Run will set PORT environment variable
ENV PORT=8080

# Run the web service
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
