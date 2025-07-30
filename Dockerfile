FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY README.md .

RUN pip install --no-cache-dir .

COPY src/ ./src/

RUN chmod +x src/main.py

ENTRYPOINT ["python", "src/main.py"]
