FROM python:3.9.1-alpine

ENV port 8080
ENV mailserver_port 2525
ENV to_pattern ".*@.*"


LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.name="MailReceiver" \
      org.label-schema.description="A web connected mail receiver" \
      org.label-schema.url="https://github.com/grro/mailreceiver_webthing" \
      org.label-schema.docker.cmd="docker run -p 8080:8080 -p 2525:2525 grro/mailreceiver"

ADD . /tmp/
WORKDIR /tmp/
RUN  python /tmp/setup.py install
WORKDIR /
RUN rm -r /tmp/

CMD mailreceiver --command listen --port $port --mailserver_port $mailserver_port --to_pattern $to_pattern
