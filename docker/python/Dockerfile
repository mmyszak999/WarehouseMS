FROM python:3.11-slim-buster

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get install -yq netcat

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["sh", "./app_scripts/db/start.sh"]