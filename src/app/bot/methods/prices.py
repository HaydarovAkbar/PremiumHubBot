import time

import telegram
from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()


def prem_message_generate(prices: Prices):
    def number_format(number):
        return f"{number:,}"[:-3]

    msg = f"""
<b>Profilga kirish orqali 👇</b>

▪️ 1 oylik obuna — {number_format(prices.with_profile_1)} so‘m 
▪️ 12 oylik obuna -  {number_format(prices.with_profile_12)} so‘m
 
<b>Profilga kirmasdan Gift sifatida xam olib beriladi 👇</b>
 
▪️ 3 oylik obuna -  {number_format(prices.with_gift_3)} so‘m
▪️ 6 oylik obuna -  {number_format(prices.with_gift_6)} so‘m
▪️ 12 oylik obuna -  {number_format(prices.with_gift_12)} so‘m
 
<code>💠 Qadrdonlaringizga hadya qilishingiz ham mumkin.</code>
"""
    return msg


def star_message_generate(prices: StarsPrices):
    def number_format(number):
        return f"{number:,}"[:-3]

    msg = f"""
<b>Ishonchli va hamyonbop narxda, 100% kafolatli Telegram Stars 🤩</b>
<i>
⭐️ 50 Stars — {number_format(prices.price_50)} so‘m 
⭐️ 75 Stars — {number_format(prices.price_75)} so‘m 
⭐️ 100 Stars — {number_format(prices.price_100)} so‘m 
⭐️ 150 Stars — {number_format(prices.price_150)} so‘m 

Qolganlari admin bilan kelishikgan holda</i>

<b>👨‍💻Sotib olish uchun admin 👉 @premium_xizmatim</b>

<b>2-3 daqiqa ichida Akkauntingizga Telegram Stars o'tkaziladi 🤝 </b>

<code>💠 Qadrdonlaringizga hadya qilishingiz ham mumkin.</code>
"""
    return msg


def get_premium_prices(update: Update, context: CallbackContext):
    all_channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for channel in all_channel:
        try:
            a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(channel)
        except Exception as e:
            print(e)
    if left_channel:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling)",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        _msg = prem_message_generate(Prices.objects.filter(is_active=True).last())
        adm_username = settings.ADMIN_USERNAME
        update.message.reply_photo(
            photo=msg.prem_photo_id,
            caption=_msg,
            parse_mode=ParseMode.HTML,
            reply_markup=keyword.admin_url(adm_username),
        )
        return state.START


def get_stars_prices(update: Update, context: CallbackContext):
    all_channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for channel in all_channel:
        try:
            a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(channel)
        except Exception as e:
            print(e)
    if left_channel:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling)",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        _msg = star_message_generate(StarsPrices.objects.filter(is_active=True).last())
        adm_username = settings.ADMIN_USERNAME
        update.message.reply_photo(
            photo=msg.star_photo_id,
            caption=_msg,
            parse_mode=ParseMode.HTML,
            reply_markup=keyword.admin_url(adm_username),
        )
        return state.START


def get_file_url(update: Update, context: CallbackContext):
    update_msg = update.message
    chat_id = update.effective_user.id

    context.bot.send_message(
        chat_id=chat_id,
        text=str(update_msg),
    )
