FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --root-user-action=ignore --upgrade pip \
  && pip install --root-user-action=ignore --no-cache-dir -r requirements.txt \
  && adduser --disabled-password --gecos '' --uid 10001 homework

USER homework

COPY main.py .

ARG PORT=8080
ARG APP_VERSION=1.0.0

EXPOSE ${PORT}
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "1", "--threads", "4", "main:app"]
