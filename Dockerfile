FROM ubuntu:18.04

RUN apt-get update && apt-get install -y supervisor python3 python3-pip gunicorn3 libsasl2-dev python3-dev libldap2-dev libssl-dev

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY src /src

COPY supervisord.conf /etc/supervisor/conf.d/

CMD supervisord -c /etc/supervisor/conf.d/supervisord.conf
