FROM robotshopdevacr.azurecr.io/baseimages/python:3.14-slim-internal

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8426", "--workers=2", "--threads=4"]