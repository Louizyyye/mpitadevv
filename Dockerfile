FROM python:3.11-slim
LABEL authors="hp"

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy static files and index.html
COPY static ./static
COPY index.html .

# Copy the rest of the application code
COPY . .

# Expose the port uvicorn will run on
EXPOSE 8000

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]