FROM python:alpine

COPY pynyaata /app/pynyaata
COPY requirements.txt /app
COPY *.py /app/
WORKDIR /app
RUN apk add build-base bash && pip install -r requirements.txt
CMD ["python", "run.py"]
