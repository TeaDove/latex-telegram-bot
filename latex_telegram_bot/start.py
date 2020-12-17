import logging
import configparser
from aiogram import Bot, Dispatcher, executor, types, utils, filters
import sympy
import cairosvg

config = configparser.ConfigParser()
config.read("secrets/config.ini")

logging.basicConfig(level=logging.WARNING)
bot = Bot(token=config['credentials']['telegram-api'])
dp = Dispatcher(bot)
HELP = open('res/help.txt', 'r').read()
START = open('res/start.txt', 'r').read()


@dp.message_handler(commands='start')
async def echo(message: types.Message):
    await message.answer(START, parse_mode='html')


@dp.message_handler(commands='help')
async def echo(message: types.Message):
    await message.answer(HELP, parse_mode='html')


@dp.message_handler(commands='p', content_types=types.ContentType.TEXT)
@dp.message_handler(filters.ChatTypeFilter(chat_type=types.chat.ChatType.PRIVATE), content_types=types.ContentType.TEXT)
async def echo(message: types.Message):
    try:
        sympy.preview(message.text, output='svg', viewer='file', filename='tmp/tmp.svg', euler=False)
    except RuntimeError:
        await message.answer('Compile error')
    else:
        cairosvg.svg2png(url='tmp/tmp.svg', write_to='tmp/tmp.png', scale=5)
        await message.reply_photo(open('tmp/tmp.png', 'rb'))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)