# syntax=docker/dockerfile:1

# This dockerfile is not working

FROM python:3.10-slim-buster

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
RUN echo "*/2 * * * * root /app/GinoProsciutto/cron.py" >> /etc/crontab

CMD [ "python3", "GinoProsciutto/main.py"]
