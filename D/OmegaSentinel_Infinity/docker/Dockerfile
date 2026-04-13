FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

EXPOSE 80

# Run the backend server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "info"]