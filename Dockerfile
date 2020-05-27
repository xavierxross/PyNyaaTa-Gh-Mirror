FROM python:slim

COPY pynyaata /app/pynyaata
COPY requirements.txt *.py /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
