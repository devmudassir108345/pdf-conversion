FROM python:3.11-slim

# Install required system libraries including libgl1 and libgthread
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

COPY . .

ENV PATH="/opt/venv/bin:$PATH"

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
