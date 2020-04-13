FROM python:alpine

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
COPY pynyaata /app/pynyaata
COPY requirements.txt /app
COPY *.py /app/
WORKDIR /app
RUN apk add build-base bash && pip install -r requirements.txt
CMD ["python", "run.py"]
