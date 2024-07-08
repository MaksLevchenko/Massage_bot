FROM python:3.11-alpine3.18

COPY requirements.txt /temp/requirements.txt

COPY .env /.env

COPY massage_bot /massage_bot

ADD /massage_bot/bot.py /massage_bot/

WORKDIR /massage_bot

RUN pip install -r /temp/requirements.txt
