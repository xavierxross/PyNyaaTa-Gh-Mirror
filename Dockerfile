FROM debian

RUN apt-get update ; apt-get -y upgrade && \
    apt-get -y install python3 python3-pip \
                       python3-flask python3-flask-sqlalchemy python3-flask-httpauth python3-flaskext.wtf \
                       python3-pymysql python3-requests python3-bs4 python3-dotenv && \
    apt-get -y --no-install-recommends install phantomjs && \
    rm -rf /var/lib/apt/lists/*
