FROM python:3.10-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy lock file and code
COPY uv.lock pyproject.toml ./
COPY main.py .

# Install dependencies using the lock file
RUN uv sync

# Cloud Run will set PORT environment variable
ENV PORT=8080

# Run the web service
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
