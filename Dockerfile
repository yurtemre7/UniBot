FROM python:3.10-slim

ADD main.py requirements.txt /bot/
ADD cogs/ /bot/cogs/
ADD util/ /bot/util/

VOLUME /data
ENV DATA_DIR=/data
ENV PYTHONHASHSEED=1337
WORKDIR /bot

RUN pip install -r requirements.txt
ENTRYPOINT python3 main.py