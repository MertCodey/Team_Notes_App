FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV FLASK_APP=app:create_app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["sh", "-c", "gunicorn -w ${WEB_CONCURRENCY:-2} -t 120 -b 0.0.0.0:${PORT:-8080} 'app:create_app()'"]
