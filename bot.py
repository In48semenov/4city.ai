# coding=utf8

import logging
import logging.config
import os
import cv2
import io

import yaml
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

from src.easyocr_model import EasyOCRModel
from src.static_text import HELLO_TEXT, NON_TARGET_TEXT, WAITING_TEXT, \
    NON_TARGET_CONTENT_TYPES, NON_LABELS_TEXT

with open("configs/logging.cfg.yml") as config_fin:
    logging.config.dictConfig(yaml.safe_load(config_fin.read()))

# Load string constants
with open("configs/menu_keyboards.yml", 'r') as file:
    messages = yaml.load(file, Loader=yaml.FullLoader)

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
model = EasyOCRModel()
keyboard_menu_options = list(messages.keys())
photo_name = ""

def generate_menu(options: list) -> types.ReplyKeyboardMarkup:
    buttons = [
        [option]
        for option in options
    ]
    keyboard_menu = types.ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    return keyboard_menu


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    text = HELLO_TEXT % user_name
    logging.info(
        f'First start from user_name = {user_name}, user_id = {user_id}')
    await message.reply(text)


@dp.message_handler(content_types=NON_TARGET_CONTENT_TYPES)
async def handle_docs_photo(message):
    user_name = message.from_user.first_name
    text = NON_TARGET_TEXT % user_name
    await message.reply(text)


@dp.message_handler(content_types=["text"])
async def text_input(message):
    signage = message.text
    chat_id = message.chat.id
    if message.text in keyboard_menu_options:
        logging.debug(open(messages[signage]["image"], 'rb'))
        photo = cv2.imread(photo_name, cv2.COLOR_BGR2RGB)
        photo_output, text_output = model(photo, messages[message.text]["image"])
        logging.debug(f"Get foto from {chat_id}")
        if text_output:
            await bot.send_photo(chat_id, photo_output)
            await bot.send_photo(message.chat.id, photo=open(photo_output, 'rb'))
        else:
            await bot.send_message(chat_id, NON_LABELS_TEXT)


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    if message.media_group_id is None:
        user_id = message.from_user.id
        message_id = message.message_id
        text = WAITING_TEXT % user_name
        logging.info(f'{user_name, user_id} is knocking to our bot')
        await bot.send_message(chat_id, text)

        global photo_name
        photo_name = './input/photo_%s_%s.jpg' % (user_id, message_id)
        await message.photo[-1].download(
            destination_file=photo_name)
        logging.debug(f"Get foto from {user_id}")
        keyboard_menu = generate_menu(keyboard_menu_options)
        await message.answer("Выберите вывеску, котрую хотите добавить на фото", reply_markup=keyboard_menu)
        # await bot.send_message(chat_id, output_text)

    else:
        text = NON_LABELS_TEXT % user_name
        await message.reply(text)


if __name__ == '__main__':
    logging.info('Bot started!')
    executor.start_polling(dp, skip_updates=True)
