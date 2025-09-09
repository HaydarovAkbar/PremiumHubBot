from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, \
    ReplyKeyboardRemove
from app.models import Channel
from ..messages.main import KeyboardText
import requests
from urllib.parse import quote

msg = KeyboardText()


class Keyboards:
    def __init__(self):
        self._keyboards = {}

    @staticmethod
    def channels(channels: List[Channel]):
        keyboards = []
        row = []

        for idx, channel in enumerate(channels, 1):
            row.append(
                InlineKeyboardButton(
                    text=channel.name,
                    url=channel.link,
                )
            )
            # Har 2 ta tugmadan keyin yangi qatorga o'tkazamiz
            if idx % 2 == 0:
                keyboards.append(row)
                row = []

        # Agar oxirgi qatorda bitta tugma qolib ketsa, uni ham qo'shamiz
        if row:
            keyboards.append(row)

        # Tekshirish tugmasini oxirida qo'shamiz
        keyboards.append(
            [InlineKeyboardButton(text='♻️ Tekshirish', callback_data='check')]
        )

        return InlineKeyboardMarkup(keyboards)

    # @staticmethod
    # def channels(channels: List[Channel]):
    #     keyboards = list()
    #     for channel in channels:
    #         keyboards.append(
    #             [
    #                 InlineKeyboardButton(
    #                     text=channel.name,
    #                     url=channel.link,
    #                 )
    #             ]
    #         )
    #     keyboards.append(
    #         [InlineKeyboardButton(text='♻️ Tekshirish', callback_data='check')]
    #     )
    #
    #     return InlineKeyboardMarkup(keyboards)

    @staticmethod
    def phone_number():
        keyboard = [KeyboardButton("📲Telefon raqamni yuborish", request_contact=True)]
        return ReplyKeyboardMarkup([keyboard], resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def base():
        _msg = msg.base['uz']
        keyboard = [
            [_msg[0]],
            [_msg[8]],
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
        share_text = f"""🎁 Sizga haligacha Telegram Premium sovgʻa qilishmadimi?

    ➖ Telegram Premium obunani sovgʻa sifatida tekinga olishni istaysizmi?

    👉 Hoziroq oʻz sovgʻangiz sari olgʻa bosing:
    {url}"""

        share_url = f"https://t.me/share/url?text={quote(share_text)}"
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
    def admin_send_url(adm_username):
        keyboard = [
            InlineKeyboardButton(
                "👮‍♀️ Adminga yuborish",
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

    @staticmethod
    def bonus():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "⭐ Kanalga ovoz berib bonus olish",
                callback_data='premium_bonus'
            )],
            [InlineKeyboardButton(
                "🫂 Guruhga odam qo'shish orqali pul ishlash",
                callback_data='add_group_bonus'
            )],
            [InlineKeyboardButton(
                "🔗 Stories bonus",
                callback_data='stories_bonus'
            )],
            [InlineKeyboardButton(
                "📤 Nickname bonus",
                callback_data='nik',
            )],
            [InlineKeyboardButton(
                "📥 Bio bonus",
                callback_data='bio'
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
            )]
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
                callback_data='story_check'
            )]
        ])

    @staticmethod
    def groups(group):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                group.name,
                url=group.link
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
            )]
        ])

    @staticmethod
    def interesting_check_bonus():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "♻️ Tekshirish",
                callback_data='nik_check'
            )]
        ])

    @staticmethod
    def interesting_check_biobonus():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "♻️ Tekshirish",
                callback_data='bio_check'
            )]
        ])

    @staticmethod
    def my_account():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🌟 Premium va stars uchun sarflash",
                callback_data='spend'
            )],
            [InlineKeyboardButton(
                "🗳 Promokod kiritish 💳",
                callback_data='add_custom_promo'
            )]
        ])

    @staticmethod
    def spend_fields(fields, current_price):
        result = list()
        field = fields[0]
        icon = "💎"
        result.append([InlineKeyboardButton(
            field.name.replace('.00', '') + ' - ' + str(field.price)[:-3] + icon,
            callback_data=str(field.id)
        )])
        helper = list()
        for field in fields[1:]:
            # icon = "💎 ✅ " if current_price >= field.price else "💎 ❌"
            helper.append(InlineKeyboardButton(
                field.name.replace('.00', '') + ' - ' + str(field.price)[:-3] + icon,
                callback_data=str(field.id)
            ))
            if len(helper) == 2:
                result.append(helper)
                helper = list()
        if helper:
            result.append(helper)
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
            )]
        ])

    @staticmethod
    def send_promo_code():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "💳 Adminga yuborish",
                callback_data='send_admin'
            )]
        ])

    @staticmethod
    def admin_base():
        return ReplyKeyboardMarkup([
            ["💠 Xabar yuborish"],
            ["🛑 Xabarni to'xtatish"],
            ["🔍 Foydalanuvchi qidirish"],
            ["📊 Umumiy Statistika", "🔓 Bandan olish"],
            ["📤 Promo kod kiritish", "💳 Promo kod tekshirish"],
            ["➕ Test qo'shish", "➖ Test o'chirish"],
            ["📈 Test Reyting", "⚙️ Test Sozlamalar"],
        ], resize_keyboard=True)

    @staticmethod
    def admin_base2():
        return ReplyKeyboardMarkup([
            # ["💠 Xabar yuborish"],
            # ["🛑 Xabarni to'xtatish"],
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
            ["📳 Davom etish"],
            ["⬅️ Orqaga"]
        ], resize_keyboard=True)

    @staticmethod
    def confirm():
        return ReplyKeyboardMarkup([
            ["✅ Tasdiqlash"]
        ], resize_keyboard=True)

    @staticmethod
    def passive():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Passiv qilish ☑️",
                callback_data='passiv'
            )]
        ])

    @staticmethod
    def adm_url(url, stat_url):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "WEB 🌐",
                url=url
            )],
            [InlineKeyboardButton(
                "WEB STATS 🌐",
                url=stat_url
            )]
        ])

    @staticmethod
    def adm_url2(url, stat_url):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "WEB 🌐",
                url=url
            )]
        ])

    @staticmethod
    def adm_user_profile():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("BANLASH", callback_data='is_ban'),
             InlineKeyboardButton("BANDAN OLISH", callback_data='no_ban'),
             ],
            [InlineKeyboardButton("BALANSE OLISH", callback_data='get_balance'),
             InlineKeyboardButton("BALANSE TO'LDIRISH", callback_data='push_balance'),
             ],
            [InlineKeyboardButton("XABAR YUBORISH", callback_data='send_msg'),
             InlineKeyboardButton("REFFERAL SISTEM", callback_data='referral'),
             ],
        ])

    @staticmethod
    def confirm_unban():
        return ReplyKeyboardMarkup([
            ["✅ Tasdiqlash", "❌ Bekor qilish"]
        ], resize_keyboard=True)
