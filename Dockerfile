FROM alpine:latest

COPY ./requirements.txt /tmp
RUN apk --no-cache --virtual .build-deps add gcc libffi-dev musl-dev openssl-dev python3-dev && \
    apk add python3 && \
    pip3 install --upgrade pip && \
    pip3 install -r /tmp/requirements.txt && \
    apk del .build-deps

COPY ./dawn /
