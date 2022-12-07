#
# Zookeeper client node demo container image
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest

RUN yum -q -y install python3

COPY python /opt/node
WORKDIR /opt/node
RUN pip3 install -r requirements.txt

CMD /usr/bin/python3 /opt/node/client.py


# EOF
