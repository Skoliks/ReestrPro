FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && sed '/^pywin32==/d' requirements.txt > /tmp/requirements-linux.txt \
    && pip install --no-cache-dir -r /tmp/requirements-linux.txt

COPY alembic ./alembic
COPY alembic.ini .
COPY backend ./backend
COPY scripts ./scripts

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
