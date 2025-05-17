FROM python:3.11-slim

# Install system dependencies including libgl1 (libGL.so.1)
RUN apt-get update && apt-get install -y libgl1

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

COPY . .

ENV PATH="/opt/venv/bin:$PATH"

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
