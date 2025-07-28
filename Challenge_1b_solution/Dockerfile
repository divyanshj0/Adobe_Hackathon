FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY main.py .
COPY processor.py .
COPY local_model/ ./local_model/
COPY input/ ./input/

# Create output directory inside container
RUN mkdir -p /app/output

# Run main script by default
CMD ["python", "main.py"]
