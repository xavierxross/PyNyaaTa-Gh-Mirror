FROM python

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get -y upgrade && apt-get -y install locales && \
    printf "en_US.UTF-8 UTF-8\nfr_FR.UTF-8 UTF-8\n" > /etc/locale.gen && \
    locale-gen && rm -rf /var/lib/apt/lists/* && \
    pip install -r requirements.txt
CMD ["python", "app.py"]
