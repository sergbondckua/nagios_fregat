FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e "s/# uk_UA.UTF-8 UTF-8/uk_UA.UTF-8 UTF-8/" /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV LANG uk_UA.UTF-8
ENV LC_ALL uk_UA.UTF-8