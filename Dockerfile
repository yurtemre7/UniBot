FROM alpine:latest

RUN apk add python3-dev py3-pip gcc musl-dev

ADD main.py requirements.txt .env /bot/
ADD cogs/ /bot/cogs/
ADD util/ /bot/util/

VOLUME /data
ENV DATA_DIR=/data
WORKDIR /bot

RUN pip install -r requirements.txt
ENTRYPOINT python3 main.py