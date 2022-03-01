from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import buy_callback

choice = InlineKeyboardMarkup(row_width=2,
                              inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text='купить грушу',
                                          callback_data=buy_callback.new(item_name='pear', quantity=1)),
                                      InlineKeyboardButton(
                                          text='купить яблоки', callback_data='buy:apple:5')
                                  ],
                                  [
                                      InlineKeyboardButton(text='отмена', callback_data='cancel')
                                  ]
                              ])

pear_keyboard = InlineKeyboardMarkup()

PEAR_LINK = 'https://kwork.ru/projects'

pear_link = InlineKeyboardButton(text='купи тут', url=PEAR_LINK)

pear_keyboard.insert(pear_link)
