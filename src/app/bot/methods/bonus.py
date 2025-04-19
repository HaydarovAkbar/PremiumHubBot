from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()

import requests


def is_premium_user(user_id: int, bot_token: str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    response = requests.post(url, data={"chat_id": user_id})

    if response.status_code == 200:
        data = response.json()
        return data.get("result", {}).get("is_premium", False)
    return False


def get_bonus_base(update: Update, context: CallbackContext):
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
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="<b>Oson va qulay imkoniyatdan foydalanib, bonuslarga ega bo‘ling! 🎁</b>",
                                 parse_mode=ParseMode.HTML,
                                 reply_markup=keyword.delete
                                 )
        _msg = """<b>Bonuslarni qo'lga kiritish uchun shartlar va vazifalar quyidagicha: 👇</b>

🔹 Shartlar va talablar bilan tanishib chiqing.
🔹 Ko‘rsatilgan vazifalarni to‘liq bajaring.
🔹 Hammasini to‘g‘ri amalga oshirganingizdan so‘ng bonuslarni qo‘lga kiriting!"""
        update.message.reply_html(
            _msg,
            reply_markup=keyword.bonus(),
        )
        return state.BONUS


def get_bonus_type(update: Update, context: CallbackContext):
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
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        query = update.callback_query
        if query.data == 'back':
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.base())
            return state.START
        elif query.data == 'premium_bonus':
            # _msg_ = "Bu tugmani faqatgina premium obunachilar ishlatoladi"
            # query.delete_message()
            # context.bot.send_message(chat_id=update.effective_user.id,
            #                          text=_msg_,
            #                          )
            user_id = update.effective_user.id
            if is_premium_user(user_id, context.bot.token):  # not
                # query.answer("Bu tugmani faqatgina premium obunachilar ishlatoladi")
                query.delete_message()
                context.bot.send_message(chat_id=user_id, text="Bu tugmani faqatgina premium obunachilar ishlatoladi")
                return
            else:
                query.delete_message()
                reward_db = RewardsChannelBoost.objects.filter(is_active=True).last()
                context.bot.send_photo(chat_id=update.effective_user.id,
                                       photo=msg.channel_boost_id,
                                       caption="<i>Quyidagi tugma orqali ovoz bering va tekshirish tugmasini bosing, har bir boost uchun bonus beriladi</i>",
                                       parse_mode=ParseMode.HTML,
                                       reply_markup=keyword.channel_boost(reward_db.channel_url)
                                       )
                return state.CHANNEL_BOOST_BONUS
        elif query.data == 'stories_bonus':
            _msg_ = "<b>👇Pastdaki WEBAPP dan foydalanib storiesingizga video joylang va 1500 so'm bonus oling.</b>"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.story_bonus(settings.STORY_URL)
                                     )
            return state.STORY_BONUS
        elif query.data == 'add_group_bonus':
            _msg_ = "Gruppaga odam qo'shadi va bonus oladi"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,

                                     )
        else:
            _msg_ = "Qiziqarli bonuslar"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_, )

    return state.BONUS


def get_daily_bonus(update: Update, context: CallbackContext):
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
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        query = update.callback_query
        if query.data == 'back':
            query.delete_message()
            _msg = """<b>Bonuslarni qo'lga kiritish uchun shartlar va vazifalar quyidagicha: 👇</b>

            🔹 Shartlar va talablar bilan tanishib chiqing.
            🔹 Ko‘rsatilgan vazifalarni to‘liq bajaring.
            🔹 Hammasini to‘g‘ri amalga oshirganingizdan so‘ng bonuslarni qo‘lga kiriting!"""
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.bonus())
            return state.BONUS
        query.delete_message()
        reward_db = RewardsChannelBoost.objects.filter(is_active=True).last()
        daily_bonus = DailyBonus.objects.filter(chat_id=update.effective_user.id, rewards_channel=reward_db)
        if daily_bonus.exists():
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Kunlik bonus bor",
                                     reply_markup=keyword.base()
                                     )
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling",
                                 reply_markup=keyword.base()
                                 )
        return state.START
    return state.BONUS
