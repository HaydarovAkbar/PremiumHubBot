from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, \
    ReplyKeyboardRemove
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
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )],
        ])

    @staticmethod
    def bonus():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "⭐ Kanalga ovoz berib bonus olish",
                callback_data='premium_bonus'
            )],
            [InlineKeyboardButton(
                "🔗 Stories bonus",
                callback_data='stories_bonus'
            )],
            [InlineKeyboardButton(
                "🫂 Guruhga odam qo'shish orqali pul ishlash",
                callback_data='add_group_bonus'
            )],
            [InlineKeyboardButton(
                "😉 Qiziqarli bonuslar",
                callback_data='qiziq_bonus'
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )],
        ])

    @staticmethod
    def channel_boost(channel_url: str):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "⭐ Ovoz berish uchun kanal",
                url=channel_url
            )],
            [InlineKeyboardButton(
                "♻️ Kunlik bonus",
                callback_data='daily_bonus'
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )],
        ])

    delete = ReplyKeyboardRemove()

    @staticmethod
    def story_bonus(webapp_url):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🔗 WEBAPP",
                web_app=WebAppInfo(url=webapp_url)
            )],
            [InlineKeyboardButton(
                "♻️ Tekshirish",
                callback_data='check'
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )],
        ])

    @staticmethod
    def groups(group):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                group.name,
                url=group.link
            )],
            [InlineKeyboardButton(
                "♻️ Tekshirish",
                callback_data='check'
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )]
        ])

    @staticmethod
    def interesting_bonus():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📤 Nickname bonus",
                callback_data='nik',
            )],
            [InlineKeyboardButton(
                "📥 Bio bonus",
                callback_data='bio'
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )]
        ])

    @staticmethod
    def interesting_check_bonus():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "♻️ Tekshirish",
                callback_data='check'
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )]
        ])

    @staticmethod
    def my_account():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Premium vs stars uchun sarflash",
                callback_data='spend'
            )]
        ])

    @staticmethod
    def spend_fields(fields, current_price):
        result = list()
        for field in fields:
            icon = "✅ " if current_price >= field.price else " ❌"
            result.append([InlineKeyboardButton(
                field.name + ' - ' + str(field.price)[:-3] + icon,
                callback_data=str(field.id)
            )])
        result.append([InlineKeyboardButton(
            "⬅️ Orqaga",
            callback_data='back'
        )])
        return InlineKeyboardMarkup(result)

    @staticmethod
    def get_promo_code():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "💳 Promokod kod harid qilish",
                callback_data='get_promo_code'
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )]
        ])

    @staticmethod
    def send_promo_code():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "💳 Adminga yuborish",
                callback_data='send_admin'
            )],
            [InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data='back'
            )]
        ])

    @staticmethod
    def admin_base():
        return ReplyKeyboardMarkup([
            ["💠 Xabar yuborish"],
            ["🔍 Foydalanuvchi qidirish"]
        ], resize_keyboard=True)

    @staticmethod
    def back():
        return ReplyKeyboardMarkup([
            ["⬅️ Orqaga"]
        ], resize_keyboard=True)

    @staticmethod
    def ads():
        return ReplyKeyboardMarkup([
            ["📳 YUBORISH"],
            ["⬅️ Orqaga"]
        ], resize_keyboard=True)
