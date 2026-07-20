FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "src.main"]