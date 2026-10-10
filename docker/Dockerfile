FROM python:3.13-slim AS builder

RUN python -m venv /opt/venv
COPY app/requirements.txt /tmp/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app/main.py ./main.py

USER 10001
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
