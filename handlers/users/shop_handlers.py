from asyncio import sleep
import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardButton, InlineKeyboardMarkup,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery)
from aiogram.utils.callback_data import CallbackData

import database
from states import shop_states
from config import lp_token, ADMINS
from loader import dp, bot, _


db = database.DBCommands()

buy_item = CallbackData('buy', 'item_id')


@dp.message_handler(CommandStart())
async def register_user(message: Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    user = await db.add_new_user(referral=referral)
    id = user.id
    bot_username = (await bot.me).username
    bot_link = f'https://t.me/{bot_username}?start={id}'
    count_users = await db.count_users()

    languages_markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(
                text='Русский',
                callback_data='lang_ru'
            )],
            [types.InlineKeyboardButton(
                text='English',
                callback_data='lang_en'
            )],
            [types.InlineKeyboardButton(
                text='Украинский',
                callback_data='lang_uk'
            )]
        ]
    )

    text = _("Приветствую вас!!\n"
             "Сейчас в базе {count_users} человек!\n"
             "\n"
             "Ваша реферальная ссылка: {bot_link}\n"
             "Проверить рефералов можно по команде: /referrals\n"
             "Просмотреть товары: /items").format(
        count_users=count_users,
        bot_link=bot_link
    )
    if message.from_user.id == ADMINS:
        text += _('\n'
                  'Добавить новый товар: /add_item')
    await message.answer(text, reply_markup=languages_markup)


@dp.callback_query_handler(text_contains='lang')
async def change_language(call: CallbackQuery):
    await call.message.edit_reply_markup()
    lang = call.data[-2:]
    await db.set_language(language=lang)
    await call.message.answer(_('Ваш язык был изменен', locale=lang))


@dp.message_handler(commands=['referrals'])
async def check_referrals(message: Message):
    referrals = await db.check_referrals()
    text = _('Ваши реферралы: \n {referrals}').format(referrals=referrals)
    await message.answer(text=text)


@dp.message_handler(commands=['items'])
async def show_items(message: Message):
    all_items = await db.show_items()
    text = _('<b>Товар</b> \t№{id}: <u>{name}</u>\n'
             '<b>Цена:</b> \t{price:,}\n')
    for item in all_items:
        markup = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(
                    text=_('Купить'),
                    callback_data=buy_item.new(item_id=item.id)
                )],
            ]
        )
        await message.answer_photo(
            photo=item.photo,
            caption=text.format(id=item.id,
                                name=item.name,
                                price=item.price/100),
            reply_markup=markup
        )
        await sleep(0.3)


@dp.callback_query_handler(buy_item.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    item_id = int(callback_data.get('item_id'))
    await call.message.edit_reply_markup()
    item = await database.Item.get(item_id)
    if not item:
        await call.message.answer(_('Такого товара не существует'))
        return
    text = _('Вы хотите купить товар \'<b>{name}</b>\' по цене <i>{price:,}/шт</i>\n'
             'Введите количество или нажмите отмена').format(name=item.name, price=item.price / 100)
    await call.message.answer(text)
    await shop_states.Purchase.EnterQuantity.set()
    await state.update_data(
        item=item,
        purchase=database.Purchase(
            item_id=item_id,
            purchase_time=datetime.datetime.now(),
            buyer=call.from_user.id
        )
    )


@dp.message_handler(regexp=r'^(\d+)$', state=shop_states.Purchase.EnterQuantity)
async def enter_quantity(message: Message, state: FSMContext):
    quantity = int(message.text)
    async with state.proxy() as data:
        data['purchase'].quantity = quantity
        item = data.get('item')
        amount = item.price * quantity
        data['purchase'].amount = amount

    agree_button = InlineKeyboardButton(text=_('Согласен'), callback_data='agree')
    change_button = InlineKeyboardButton(text=_('Ввести количество заново'), callback_data='change')
    cancel_button = InlineKeyboardButton(text=_('Отменить покупку'), callback_data='cancel')
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [agree_button],
            [change_button],
            [cancel_button]
        ]
    )
    await message.answer(
        _('Хорошо, вы хотите купить <i>{quantity}</i> {name} по цене <b>{price:,}/шт</b> '
          'Получится <b>{amount:,}</b>. Подтверждаете?').format(
            quantity=quantity,
            name=item.name,
            amount=amount / 100,
            price=item.price/100),
        reply_markup=markup
    )
    await shop_states.Purchase.Approval.set()


@dp.message_handler(state=shop_states.Purchase.EnterQuantity)
async def wrong_quantity(message: Message):
    await message.answer(_('Неверное значение, введите число'))


@dp.callback_query_handler(text_contains='cancel', state=shop_states.Purchase)
async def cancel_purchase(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer(_('Вы отменили эту покупку'))
    await state.reset_state()


@dp.callback_query_handler(text_contains='change', state=shop_states.Purchase.Approval)
async def change_purchase(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer(_("Введите количество товара заново."))
    await shop_states.Purchase.EnterQuantity.set()


@dp.callback_query_handler(text_contains='agree', state=shop_states.Purchase.Approval)
async def agree_purchase(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    purchase = data.get('purchase')
    item = data.get('item')
    await purchase.create()
    await call.message.answer(
        _('Хорошо, оплатите <b>{amount:,}</b> по методу указанному ниже и нажмите '
          'на кнопку ниже').format(amount=purchase.amount / 100)
    )
    currency = 'RUB'
    need_name = True
    need_phone_number = False
    need_email = False
    need_shipping_address = True

    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=item.name,
        description=item.name,
        payload=str(purchase.id),
        start_parameter=str(purchase.id),
        currency=currency,
        prices=[
            LabeledPrice(label=item.name,
                         amount=purchase.amount)
        ],
        provider_token=lp_token,
        need_email=need_email,
        need_name=need_name,
        need_phone_number=need_phone_number,
        need_shipping_address=need_shipping_address
    )
    await state.update_data(purchase=purchase)
    await shop_states.Purchase.Payment.set()


@dp.pre_checkout_query_handler(state=shop_states.Purchase.Payment)
async def checkout(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)
    data = await state.get_data()
    purchase: database.Purchase = data.get('purchase')
    success = await check_payment(purchase)
    if success:
        await purchase.update(
            successful=True,
            shipping_address=query.order_info.shipping_address.to_python()
            if query.order_info.shipping_address else None,
            phone_number=query.order_info.phone_number,
            receiver=query.order_info.name,
            email=query.order_info.email
        ).apply()
        await state.reset_state()
        await bot.send_message(chat_id=query.from_user.id,
                               text=_('Спасибо за покупку'))
    else:
        await bot.send_message(chat_id=query.from_user.id,
                               text=_('Покупка не была подтверждена, попробуйте позже'))


async def check_payment(purchase: database.Purchase):
    return True


