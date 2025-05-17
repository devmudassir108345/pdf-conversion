# Base image - Python 3.11 slim version
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for your packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt to container
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of your app code to container
COPY . .

# Expose port if using Flask default port (optional)
EXPOSE 5000

# Run your app (change app.py if your main file is different)
CMD ["python", "app.py"]
