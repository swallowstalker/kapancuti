FROM python:3.6.5-jessie

RUN apt-get update
RUN apt-get install -y locales
RUN echo "id_ID.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen

ENV LC_ALL id_ID.UTF-8
ENV LANG id_ID.UTF-8
ENV LANGUAGE id_ID.UTF-8

RUN mkdir /app
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD python server.py
