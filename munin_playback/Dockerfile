FROM python:3.7.1-alpine3.8

RUN apk add --update --no-cache g++ gcc libxslt-dev libffi-dev libressl-dev tzdata netcat-openbsd

RUN echo $TZ > /etc/timezone

ADD requirements.txt /
RUN pip install -r requirements.txt

RUN mkdir /playback
WORKDIR /playback

RUN wb-manager init munin

CMD wayback -a -p 8080 -b 0.0.0.0 -t 2 --auto-interval 120