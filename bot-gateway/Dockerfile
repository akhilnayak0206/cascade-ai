FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir uv && \
    uv venv && \
    uv pip install .

COPY src/ ./src/

CMD ["uv","run","python", "-m", "src.main"]