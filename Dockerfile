# # Base image - Python 3.11 slim version
# FROM python:3.11-slim

# # Set working directory inside container
# WORKDIR /app

# # Install system dependencies needed for your packages
# RUN apt-get update && apt-get install -y \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     libsm6 \
#     libxext6 \
#     libxrender1 \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements.txt to container
# COPY requirements.txt .

# # Install Python dependencies from requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy rest of your app code to container
# COPY . .

# # Expose port if using Flask default port (optional)
# EXPOSE 5000

# # Run your app (change app.py if your main file is different)
# CMD ["python", "app.py"]



# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install LibreOffice and required system libraries
RUN apt-get update && apt-get install -y \
    libreoffice \
    libgl1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port (optional: if using Flask app)
EXPOSE 5000

# Run using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
