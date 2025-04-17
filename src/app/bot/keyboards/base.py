from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from app.models import Channel
from ..messages.main import KeyboardText

msg = KeyboardText()


class Keyboards:
    def __init__(self):
        self._keyboards = {}

    @staticmethod
    def channels(channels: List[Channel]):
        keyboards = list()
        for channel in channels:
            keyboards.append(
                [
                    InlineKeyboardButton(
                        text=channel.name,
                        url=channel.link,
                    )
                ]
            )
        keyboards.append(
            [InlineKeyboardButton(text='♻️ Tekshirish', callback_data='check')]
        )

        return InlineKeyboardMarkup(keyboards)

    @staticmethod
    def phone_number():
        keyboard = [KeyboardButton("📲Telefon raqamni yuborish", request_contact=True)]
        return ReplyKeyboardMarkup([keyboard], resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def base():
        _msg = msg.base['uz']
        keyboard = [
            [_msg[0]],
            [_msg[1], _msg[2]],
            [_msg[3]],
            [_msg[4], _msg[5]],
            [_msg[6], _msg[7]]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def signup(url):
        keyboard = [
            [InlineKeyboardButton("📮 Ro’yxatdan o’tish", web_app=WebAppInfo(url=url))]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def referral(url):
        share_text = (
            "🎁 Hoziroq oʻz sovgʻangiz sari olgʻa bosing:\n"
        )
        share_url = f"https://t.me/share/url?url={url}&text={share_text}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Doʻstlarga ulashish", url=share_url)]
        ])

        return keyboard

    @staticmethod
    def admin_url(adm_username):
        keyboard = [
            InlineKeyboardButton(
                "🌟 Premium sotib olish",
                url=f"https://t.me/{adm_username}"
            )
        ]
        return InlineKeyboardMarkup([keyboard])

    @staticmethod
    def rating():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🏆 TOP Reyting",
                callback_data='top_rating'
            )],
            [InlineKeyboardButton(
                "🏆 Haftalik TOP Reyting",
                callback_data='weekly_rating'
            )]
        ])
