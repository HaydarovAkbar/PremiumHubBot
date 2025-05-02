from datetime import datetime

from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts, Group, CustomUserAccount
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
import requests

keyword = Keyboards()
state = States()
msg = MessageText()


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
            user_id = update.effective_user.id
            if not is_premium_user(user_id, context.bot.token):  # not
                # query.answer("Bu tugmani faqatgina premium obunachilar ishlatoladi")
                query.delete_message()
                context.bot.send_message(chat_id=user_id, text="Bu tugmani faqatgina premium obunachilar ishlatoladi")
                return state.BONUS
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
            story_bonus_price = StoryBonusPrice.objects.filter(is_active=True).last()
            _msg_ = f"<b>👇Pastdaki WEBAPP dan foydalanib storiesingizga video joylang va {story_bonus_price.price} so'm bonus oling.</b>"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.story_bonus(settings.STORY_URL)
                                     )
            return state.STORY_BONUS
        elif query.data == 'add_group_bonus':
            query.delete_message()
            group = Group.objects.filter(is_active=True).last()
            if group:
                _msg_ = f"""<b>Quyidagi guruhga kamida {group.limit} ta do'stlaringiz qo'shing va {group.price} so'm bonusga ega bo'ling: 👇</b>"""
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text=_msg_,
                                         parse_mode="HTML",
                                         reply_markup=keyword.groups(group)
                                         )
                return state.GROUP_BONUS
            else:
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text="👇 Hozircha bonus uchun guruh kiritilmagan!",
                                         parse_mode="HTML",
                                         reply_markup=keyword.groups(group)
                                         )
        else:
            _msg_ = "<b>Quyidagi qiziqarli vazifalarni bajarib bonuslar oling.</b>"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_bonus()
                                     )
            return state.INTERESTING_BONUS

    return state.BONUS


def get_user_boosts(chat_id, user_id):
    payload = {
        "chat_id": chat_id,  # "@channelusername" yoki integer
        "user_id": user_id
    }
    API_URL = f"https://api.telegram.org/bot{settings.TOKEN}/getUserChatBoosts"
    response = requests.post(API_URL, json=payload)

    if response.ok:
        data = response.json()
        if data.get("ok"):
            return data["result"]
    return False


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
        daily_bonus, _ = DailyBonus.objects.get_or_create(chat_id=update.effective_user.id, rewards_channel=reward_db)

        def extract_channel_username(url: str) -> str:
            if url.startswith("https://t.me/"):
                return url.split("https://t.me/")[-1].split("/")[0].strip("@")
            return url.strip("@")

        boost_count = get_user_boosts(extract_channel_username(reward_db.channel_url), update.effective_user.id)
        if not boost_count:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=f"❌ Siz kanalimizga boost bermagansiz xali !)",
                                     reply_markup=keyword.base()
                                     )
            return state.START
        if not _:
            if daily_bonus.last_bonus != datetime.today().date():
                daily_bonus.last_bonus = datetime.today().date()
                daily_bonus.save()
                custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
                custom_account.current_price = reward_db.daily_bonus
                custom_account.save()
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text=f"🎉 Tabriklaymiz sizga {reward_db.daily_bonus} so'm kunlik bonus berildi.",
                                         reply_markup=keyword.base()
                                         )
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Kunlik bonus allaqachon olgansiz!",
                                     reply_markup=keyword.base()
                                     )
        custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
        custom_account.current_price = reward_db.elementary_bonus
        custom_account.save()
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text=f"🎉 Tabriklaymiz sizga {reward_db.elementary_bonus} so'm kanalimizga ovoz berganingiz uchun bonus berildi.",
                                 reply_markup=keyword.base()
                                 )
        return state.START
    return state.BONUS


def get_stories_bonus(update: Update, context: CallbackContext):
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
        story_db = StoryBonusPrice.objects.filter(is_active=True).last()
        story_bonus = StoryBonusAccounts.objects.filter(chat_id=update.effective_user.id)
        if story_bonus.exists():
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Siz allaqachon bonus olgansiz!",
                                     reply_markup=keyword.base()
                                     )
            return state.STORY_BONUS
        stories_counter = context.chat_data.get('stories_counter', 0)
        context.chat_data['stories_counter'] = stories_counter + 1
        if context.chat_data['stories_counter'] > 2:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.bonus()
                                     )
            custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
            custom_account.current_price = story_db.price
            custom_account.save()
            StoryBonusAccounts.objects.create(chat_id=update.effective_user.id)
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=f"🎉 Tabriklaymiz sizga {story_db.price} so'm kanalimizga ovoz berganingiz uchun bonus berildi.",
                                     )
        else:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Tekshirilmoqda iltimos keyinroq urinib ko'ring 🕞",
                                     reply_markup=keyword.bonus()
                                     )
        return state.STORY_BONUS
    return state.BONUS
