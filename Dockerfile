FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl git libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install -e ".[dev]"

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.events_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]