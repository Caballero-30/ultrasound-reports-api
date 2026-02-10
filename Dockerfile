FROM python:3.11-slim AS builder
LABEL authors="richard.caballero"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
LABEL authors="richard.caballero"

WORKDIR /app

COPY --from=builder /install/ /usr/local/

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir /app"
