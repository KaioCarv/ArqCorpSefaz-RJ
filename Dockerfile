FROM python:3.11-slim

WORKDIR /app

# dependências do sistema (certs + build básico)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# libs Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# código
COPY . .

EXPOSE 8000
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]
