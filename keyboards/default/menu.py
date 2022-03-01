from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

menu =ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='first')
        ],
        [
            KeyboardButton(text='second'),
            KeyboardButton(text='third')
        ]
    ],
    resize_keyboard=True
)
