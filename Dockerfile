FROM swallowstalker/kapancuti-base:1.0.0

COPY . /app

CMD python server_inline.py
