FROM python:3.8.6-buster

WORKDIR /bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD python bot.py 1>/dev/stdout 2>/dev/stderr 