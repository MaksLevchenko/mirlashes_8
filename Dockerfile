FROM python:3.11-alpine3.18

COPY requirements.txt /temp/requirements.txt

COPY .env /.env

COPY lashes_bot /lashes_bot

ADD /lashes_bot/bot.py /lashes_bot/

WORKDIR /lashes_bot

RUN pip install -r /temp/requirements.txt
