FROM ubuntu:16.04

MAINTAINER mourad mourafiq <mouradmourafiq@gmail.com>

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -y update && apt-get install -y --no-install-recommends \
        python3.5 \
        python3.5-dev \
        python3-setuptools \
        python3-pip \
    && apt-get autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install and Upgrade pip to the latest version
RUN pip3 install --upgrade setuptools pip

# copy requirements.txt
COPY requirements.txt /setup/
RUN pip3 install --no-cache-dir -r /setup/requirements.txt

VOLUME /polyaxon
WORKDIR /polyaxon
copy . /polyaxon

CMD python3 polyaxon_events/events.py
