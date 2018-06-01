FROM python:3.6.5-alpine3.7

RUN mkdir /app
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD python server.py
