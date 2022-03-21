from typing import Union

from loader import dp
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from keyboards.default import menu
from aiogram.dispatcher.filters import Command, Text


@dp.message_handler(Command('menu'))
async def show_menu(message: Message):
    await list_categories(message=message)
    await message.answer('Получилось, получается', reply_markup=menu)


# @dp.message_handler(Text(equals=['first', 'second', 'third']))
# async def get_food(message: Message):
#     await message.answer(f'вы выбарли {message.text} кнопку', reply_markup=ReplyKeyboardRemove())


async def list_categories(message: Union[Message, CallbackQuery], **kwargs):
    markup = await categories_keyboard()