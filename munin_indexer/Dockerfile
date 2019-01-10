FROM python:3.7.1-alpine3.8

RUN apk add --update --no-cache g++ gcc libxslt-dev tzdata netcat-openbsd git

RUN echo $TZ > /etc/timezone

ADD requirements.txt /
RUN pip install -r requirements.txt

RUN mkdir /worker
ADD ./worker/* /worker/
WORKDIR /worker
CMD ["python", "worker.py"]
