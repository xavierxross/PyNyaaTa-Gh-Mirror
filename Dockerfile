FROM debian

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN apt-get update && apt-get -y upgrade && apt-get install curl && \
    curl -sSL https://deb.nodesource.com/setup_12.x | bash - && \
    apt-get -y install python3 python3-pip locales nodejs \
                       python3-flask python3-flask-sqlalchemy python3-flask-httpauth python3-flaskext.wtf \
                       python3-pymysql python3-requests python3-bs4 python3-dotenv && \
    pip3 install cfscrape && \
    printf "en_US.UTF-8 UTF-8\nfr_FR.UTF-8 UTF-8\n" > /etc/locale.gen && \
    locale-gen && rm -rf /var/lib/apt/lists/*
