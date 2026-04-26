FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SECRET_KEY=docker-build-secret \
    DJANGO_DEBUG=false \
    DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,backend,proxy \
    MYSQL_DATABASE=modern_sis \
    MYSQL_USER=modern_sis \
    MYSQL_PASSWORD=modern_sis \
    MYSQL_HOST=db \
    MYSQL_PORT=3306

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt ./requirements/base.txt

RUN pip install --upgrade pip \
    && PIP_DEFAULT_TIMEOUT=300 pip install --retries 5 --timeout 300 -r requirements/base.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "sis_backend.wsgi:application"]
