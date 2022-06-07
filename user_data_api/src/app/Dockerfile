FROM python:3.9-alpine

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update && \
    apk add build-base librdkafka-dev && \
    apk --no-cache add curl && \
    pip install --upgrade pip && \
    pip install -U setuptools


COPY requirements.txt .
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

EXPOSE 8011

COPY . ./app

