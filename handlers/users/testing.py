from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.filters import Command

from loader import dp
from states.test import Test


@dp.message_handler(Command('test'), state=None)
async def enter_test(message: types.Message):
    await message.answer('ответь на вопрос: Ты дебил?')

    await Test.Q1.set()


@dp.message_handler(state=Test.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text

    await state.update_data(answer1=answer)

    await message.answer('а ты придурок?')
    await Test.next()


@dp.message_handler(state=Test.Q2)
async def answer_q2(message: types.Message, state:FSMContext):
    answer2 = message.text
    data = await state.get_data()
    answer1 = data.get('answer1')

    await message.answer('Спасибо, что отвечал честно')
    await state.finish()
