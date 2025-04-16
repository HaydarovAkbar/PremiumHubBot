from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from app.models import Channel


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
        keyboard = [
            ["🌟 Bepul Premium va Stars olish 🌟"],
            ["💸 Premium narxlari", "🌟 Premium sotib olish"],
            ["⭐ Stars Narxlari"],
            ["🏆 TOP Reyting", "🎉 Top Reytinglar"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def signup(url):
        keyboard = [
            [InlineKeyboardButton("📮 Ro’yxatdan o’tish", web_app=WebAppInfo(url=url))]
        ]
        return InlineKeyboardMarkup(keyboard)
