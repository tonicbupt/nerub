FROM alpine:latest

RUN apk --update add python py-setuptools iproute2 && \
    apk add --virtual build-dependencies git python-dev build-base curl bash py-pip alpine-sdk libffi-dev openssl-dev

COPY requirements.txt /
COPY nerub /nerub
COPY gunicorn_config.py /

RUN pip install -r requirements.txt
RUN apk del build-dependencies && rm -rf /var/cache/apk/*

WORKDIR /
CMD ["gunicorn", "-c", "gunicorn_config.py", "nerub.plugin:app"]
