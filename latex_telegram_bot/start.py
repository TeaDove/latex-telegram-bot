import logging
import configparser
from aiogram import Bot, Dispatcher, executor, types, utils, filters
import sympy
import cairosvg
from PIL import Image

config = configparser.ConfigParser()
config.read("secrets/config.ini")

logging.basicConfig(level=logging.WARNING)
bot = Bot(token=config['credentials']['telegram-api'])
dp = Dispatcher(bot)
HELP = open('res/help.txt', 'r').read()
START = open('res/start.txt', 'r').read()


def compile_tex(latex: str):
    try:
        #         preamble = r"""\documentclass[pdf, unicode, 12pt, a4paper,oneside,fleqn]{article}
        # \usepackage[utf8]{inputenc}
        # \begin{document}"""
        #TODO Добавить Русский язык
        sympy.preview(latex, output='svg', viewer='file', filename='tmp/image.svg', euler=False)
    except RuntimeError as error:
        return False, error
    else:
        return True, None


def make_png():
    cairosvg.svg2png(url='tmp/image.svg', write_to='tmp/image.png', scale=5, background_color='#ffffff')

    old_im = Image.open('tmp/image.png')
    old_size = old_im.size
    new_size = (int(old_size[0] // 0.83), int(old_size[1] // 0.83))
    if  0.05 <= new_size[0] / new_size[1] <= 20:
        new_im = Image.new("RGB", new_size, color=16777215)
        new_im.paste(old_im, ((new_size[0] - old_size[0]) // 2,
                              (new_size[1] - old_size[1]) // 2))
        new_im.save('tmp/image.png')
        return True
    else:
        return False


@dp.message_handler(commands='start')
async def echo(message: types.Message):
    await message.answer(START, parse_mode='html')


@dp.message_handler(commands='help')
async def echo(message: types.Message):
    await message.answer(HELP, parse_mode='html')


@dp.message_handler(lambda msg: len(msg.text.split()) > 1, commands='s', content_types=types.ContentType.TEXT)
async def echo(message: types.Message):
    compiled, err = compile_tex(message.text[message.text.find(' '):])
    if compiled:
        await message.reply_document(open('tmp/image.svg', 'rb'))
    else:
        await message.reply(f'Compile error\n')


@dp.message_handler(lambda msg: len(msg.text.split()) > 1, commands='p', content_types=types.ContentType.TEXT)
async def echo(message: types.Message):
    compiled, err = compile_tex(message.text[message.text.find(' '):])
    if compiled:
        if make_png():
            await message.reply_photo(open('tmp/image.png', 'rb'))
        else:
            await message.reply('Wrong image size, can only send as svg')
    else:
        await message.reply(f'Compile error\n')


@dp.message_handler(lambda msg: len(msg.text.split()) > 1, commands='d', content_types=types.ContentType.TEXT)
@dp.message_handler(filters.ChatTypeFilter(chat_type=types.chat.ChatType.PRIVATE), content_types=types.ContentType.TEXT)
async def echo(message: types.Message):
    if message.chat.type == types.chat.ChatType.PRIVATE:
        compiled, err = compile_tex(message.text)
    else:
        compiled, err = compile_tex(message.text[message.text.find(' '):])
    if compiled:
        if True:
            if make_png():
                await message.reply_photo(open('tmp/image.png', 'rb'))
            else:
                await message.reply('Wrong image size, can only send as svg')
        else:
            await message.reply_document(open('tmp/image.svg', 'rb'))
    else:
        await message.reply(f'Compile error\n, {err}')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
