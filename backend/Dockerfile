# Backend image for the ChatYourNotes Flask service
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        git \
        libgomp1 \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Optional: install uv for local workflows inside the container
RUN curl -fsSL https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.local/bin/uv /usr/local/bin/uv

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/pyproject.toml ./pyproject.toml
COPY backend/app ./app
COPY backend/main.py ./main.py

ENV FLASK_APP=main.py
EXPOSE 8000

CMD ["python", "main.py"]
