FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential python3-dev \
    && python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

COPY . .

ENV PATH="/opt/venv/bin:$PATH"

CMD ["gunicorn", "app:app"]
