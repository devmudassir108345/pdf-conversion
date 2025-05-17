# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install LibreOffice and required system libraries
RUN apt-get update && apt-get install -y \
    libreoffice \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
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
