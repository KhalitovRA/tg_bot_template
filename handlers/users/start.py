# # from aiogram import types
# # from aiogram.dispatcher.filters.builtin import CommandStart
# #
# # from loader import dp
#
# #
# # @dp.message_handler(CommandStart())
# # async def bot_start(message: types.Message):
# #     await message.answer(f"Привет, {message.from_user.full_name}!")
# from random import randint
#
# from aiogram import types
# from asyncpg import Connection, Record, UniqueViolationError
#
# from loader import bot, db, dp
#
#
# class DBCommands:
#     pool: Connection = db
#     ADD_NEW_USER = "INSERT INTO users(chat_id, username, full_name) VALUES ($1, $2, $3) RETURNING id"
#     ADD_NEW_USER_REFERRAL = "INSERT INTO users(chat_id, username, full_name, referral) " \
#                             "VALUES ($1, $2, $3, $4 ) RETURNING id"
#     COUNT_USERS = "SELECT COUNT(*) FROM users"
#     GET_ID = "SELECT id FROM users WHERE chat_id = $1"
#     CHECK_REFERRALS = "SELECT chat_id FROM users WHERE referral=" \
#                         "(SELECT id FROM users WHERE chat_id=$1)"
#     CHECK_BALANCE = "SELECT balance FROM users WHERE chat_id = $1"
#     ADD_MONEY = "UPDATE users SET balance=balance+$1 WHERE chat_id=$2"
#
#     async def add_new_user(self, referral=None):
#         user = types.User.get_current()
#
#         chat_id = user.id
#         username = user.username
#         full_name = user.full_name
#         args = chat_id, username, full_name
#
#         if referral:
#             args += (int(referral), )
#             command = self.ADD_NEW_USER_REFERRAL
#         else:
#             command = self.ADD_NEW_USER
#
#         try:
#             record_id = await self.pool.fetchval(command, *args)
#             return record_id
#         except UniqueViolationError:
#             pass
#
#     async def count_users(self):
#         record: Record = await self.pool.fetchval(self.COUNT_USERS)
#         return record
#
#     async def get_id(self):
#         command = self.GET_ID
#         user_id = types.User.get_current().id
#         return await self.pool.fetchval(command, user_id)
#
#     async def check_referrals(self):
#         user_id = types.User.get_current().id
#         command = self.CHECK_REFERRALS
#         rows = await self.pool.fetch(command, user_id)
#         return ", ".join([
#             f"{num + 1}. " + (await bot.get_chat(user["chat_id"])).get_mention(as_html=True)
#             for num, user in enumerate(rows)
#         ])
#
#     async def check_balance(self):
#         command = self.CHECK_BALANCE
#         user_id = types.User.get_current()
#         return await self.pool.fetchval(command, user_id)
#
#     async def add_money(self, money):
#         command = self.ADD_MONEY
#         user_id = types.User.get_current()
#         return await self.pool.fetchval(command, money, user_id)
#
#
# database = DBCommands()
#
#
# @dp.message_handler(commands=['start'])
# async def register_user(message: types.Message):
#     chat_id = message.from_user.id
#     referral = message.get_args()
#     id = await database.add_new_user(referral=referral)
#     count_users = await database.count_users()
#     text = ""
#
#     if not id:
#         id = await database.get_id()
#     else:
#         text = "Записал в базу."
#     bot_username = (await bot.get_me()).username
#     id_referral = id
#     bot_link = f"https://t.me/{bot_username}?/start={id_referral}"
#     balance = await database.check_balance()
#     text += f"""
# Сейчас в базе {count_users} человек!
#
# Ваша реферальная ссылка: {bot_link}
# Проверить реферралов можно по команде: /referrals
#
# Ваш баланс: {balance} монет.
# Добавить монет: /add_money
# """
#     await bot.send_message(chat_id, text)
#
#
# @dp.message_handler(commands=["referrals"])
# async def check_referrals(message: types.Message):
#     referrals = await database.check_referrals()
#     text = "Ваши реферралы: \n" + referrals
#     await message.answer(text)
#
#
# @dp.message_handler(commands=['add_money'])
# async def add_money(message: types.Message):
#     random_amount = randint(1, 100)
#     await database.add_money(random_amount)
#     balance = await database.check_balance()
#     text = f"Вам было добавлено {random_amount} монет. \nТеперь ваш баланс: {balance}"
#     await message.answer(text)
