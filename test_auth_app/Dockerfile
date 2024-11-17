FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ /app/

ENV PYTHONPATH=/app

RUN python manage.py collectstatic --noinput || true
RUN python manage.py makemigrations || true
RUN python manage.py migrate || true

EXPOSE 8000

CMD ["uvicorn", "TestAuthApp.asgi:application", "--host", "0.0.0.0", "--port", "8000"]