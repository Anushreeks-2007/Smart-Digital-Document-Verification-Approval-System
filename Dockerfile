FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app/uploads

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "python -c 'from database.db import initialize_database; initialize_database()' && flask --app run:app run --host=0.0.0.0 --port=5000"]
