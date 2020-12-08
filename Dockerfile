FROM python:3.9.1-slim

COPY pynyaata /app/pynyaata
COPY requirements.txt *.py /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
