# Use AMD64-compatible slim Python base image
FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Copy only requirements first for efficient caching
COPY 1a/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY 1a/ .

# Set the default command to run your main script
CMD ["python", "main.py"]
