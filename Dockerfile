FROM polyaxon/polyaxon-base

MAINTAINER mourad mourafiq <mouradmourafiq@gmail.com>

# copy requirements.txt
COPY requirements.txt /setup/
RUN pip3 install --no-cache-dir -r /setup/requirements.txt

VOLUME /polyaxon_events
WORKDIR /polyaxon_events
copy . /polyaxon_events

ENV PYTHONPATH /polyaxon_events

# To set directly on the chart yaml files
#CMD python3 -u polyaxon_events/events/sidecar.py
