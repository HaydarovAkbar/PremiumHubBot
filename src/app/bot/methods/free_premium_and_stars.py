import time

import telegram
from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
import requests

keyword = Keyboards()
state = States()
msg = MessageText()


def generate_link(chat_id):
    USERNAME = settings.USERNAME
    CHAT_ID = chat_id
    return f'https://t.me/{USERNAME}?start={CHAT_ID}'


def get_free_premium_and_stars(update: Update, context: CallbackContext):
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
        url = generate_link(update.effective_user.id)
        photo_id = msg.prem_photo_id
        caption = msg.GET_PREMIUM_AND_STARS.replace('URL', url)
        markup = keyword.referral(url).to_dict()
        requests.post(
            f"https://api.telegram.org/bot{settings.TOKEN}/sendPhoto",
            json={
                "chat_id": user_db.chat_id,
                "photo": photo_id,
                "caption": caption,
                "parse_mode": "HTML",
                "reply_markup": markup,
                'message_effect_id': "5104841245755180586"
            }
        )
        return state.START


def get_file_url(update: Update, context: CallbackContext):
    update_msg = update.message
    if CustomUser.objects.get(chat_id=update_msg.from_user.id, is_admin=True):

        chat_id = update.effective_user.id

        context.bot.send_message(
            chat_id=chat_id,
            text=str(update_msg),
        )
        return state.START
