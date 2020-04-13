FROM python:alpine

COPY pynyaata /app/pynyaata
COPY requirements.txt /app
COPY *.py /app/
WORKDIR /app
RUN apk add build-base && pip install -r requirements.txt && apk del build-base
CMD ["python", "run.py"]
