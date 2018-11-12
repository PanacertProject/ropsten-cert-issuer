FROM seegno/bitcoind:0.13-alpine

ENV APP_HOME /panacert-issuer

RUN mkdir $APP_HOME
ADD . $APP_HOME
WORKDIR $APP_HOME

RUN apk add --update \
        bash \
        ca-certificates \
        curl \
        gcc \
        gmp-dev \
        libffi-dev \
        libressl-dev \
        linux-headers \
        make \
        musl-dev \
        python \
        python3 \
        python3-dev \
        tar \
    && python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools \
    && pip3 install /panacert-issuer/. \
    && pip3 install -U flask-cors \
    && rm -r /usr/lib/python*/ensurepip \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache \
    && sed -i.bak s/==1\.0b1/\>=1\.0\.2/g /usr/lib/python3.*/site-packages/merkletools-1.0.2-py3.*.egg-info/requires.txt \
    && source setup.sh

# ENTRYPOINT bash
CMD ["python3", "app.py"]