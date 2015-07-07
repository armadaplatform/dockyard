FROM microservice_python
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV DOCKYARD_APT_GET_UPDATE_DATE 2015-01-16

RUN apt-get update
RUN apt-get install -y build-essential libevent-dev liblzma-dev nginx
RUN apt-get install -y python-m2crypto swig libssl-dev

RUN pip install -U docker_registry
RUN pip install -U docker-registry[bugsnag]
RUN pip install -U htpasswd

ADD . /opt/dockyard
ADD ./supervisor/dockyard.conf /etc/supervisor/conf.d/dockyard.conf
RUN rm -f /etc/nginx/sites-enabled/default

RUN rm -f /etc/supervisor/conf.d/update_haproxy.conf

EXPOSE 80
