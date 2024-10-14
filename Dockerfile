FROM --platform=linux/amd64 python:3.10.9-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

COPY modules/Linux/64/ /usr/lib/

ENV LD_LIBRARY_PATH=/usr/lib

RUN apt-get update; \
    apt-get install -y gettext;

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
