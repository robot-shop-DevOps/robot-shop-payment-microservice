FROM robotshopdevacr.azurecr.io/baseimages/python:3.14-slim-internal

WORKDIR /app

COPY payment/ ./payment

RUN pip install --no-cache-dir -r payment/requirements.txt

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8426", "--workers=2", "--threads=4"]