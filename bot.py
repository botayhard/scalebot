import io
import requests
from PIL import Image
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
token = os.getenv("TOKEN")

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def halp(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Умею приводить картинки к виду, который вписывается в квадрат 512x512 (одна сторона — 512 пикселей, другая — 512 или меньше). Но только в личных сообщениях.")


start = CommandHandler('start', halp, run_async=True)
dispatcher.add_handler(start)
help = CommandHandler('help', halp, run_async=True)
dispatcher.add_handler(help)


def sizecalc(h, w):
    if h > w:
        f = 512/h
    else:
        f = 512/w
    return int(h*f), int(w*f)


def scaler(update, context):
    try:
        url = update.message.effective_attachment.get_file().file_path
    except AttributeError:
        url = context.bot.get_file(update.message.photo[-1]).file_path
    data = requests.get(url).content
    img = Image.open(io.BytesIO(data))
    img_512 = img.resize(sizecalc(img.size[0], img.size[1]))
    img_bit = io.BytesIO()
    img_bit.name = 'result.png'
    img_512.save(img_bit, 'PNG')
    img_bit.seek(0)
    context.bot.send_document(
        chat_id=update.message.chat_id, document=img_bit, filename='result.png')


photo = MessageHandler(
    Filters.photo & Filters.chat_type.private, scaler, run_async=True)
dispatcher.add_handler(photo)
image = MessageHandler(Filters.document.category(
    "image") & Filters.chat_type.private, scaler, run_async=True)
dispatcher.add_handler(image)

updater.start_polling()
