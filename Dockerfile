FROM python:3.10-slim

ADD requirements.txt /bot/
RUN pip install -r /bot/requirements.txt

ADD main.py /bot/
ADD cogs/ /bot/cogs/
ADD util/ /bot/util/

VOLUME /data
ENV DATA_DIR=/data
ENV PYTHONHASHSEED=1337
WORKDIR /bot

ENTRYPOINT python3 main.py
