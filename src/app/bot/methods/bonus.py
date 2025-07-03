from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts, Group, CustomUserAccount, TopUser, InterestingBonus
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
import requests

keyword = Keyboards()
state = States()
msg = MessageText()

def is_premium_user_check(user_id: int, bot_token: str, chat_id: int) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
    response = requests.get(url, params={
        "chat_id": chat_id,
        "user_id": user_id
    })

    if response.status_code == 200:
        data = response.json()
        return data.get("result", {}).get("user", {}).get("is_premium", False)
    return False


def is_premium_user(user_id: int, bot_token: str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
    response = requests.get(url, params={
        "chat_id": user_id,
        "user_id": user_id
    })

    if response.status_code == 200:
        data = response.json()
        return data.get("result", {}).get("user", {}).get("is_premium", False)
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
        msg = """<b>Bonuslarni qo'lga kiritish uchun shartlar va vazifalar quyidagicha: 👇</b>
        
🔹 Shartlar va talablar bilan tanishib chiqing.
🔹 Ko‘rsatilgan vazifalarni to‘liq bajaring.
🔹 Hammasini to‘g‘ri amalga oshirganingizdan so‘ng bonuslarni qo‘lga kiriting!
        """
        photo_id= 'AgACAgIAAxkBAAI4lGhT2UmTBZEJ7Jy5KXcmQsq-oes-AAKe8DEbAT-hSgtb12QkY0ADAQADAgADeQADNgQ'


        requests.post(
            f"https://api.telegram.org/bot{settings.TOKEN}/sendPhoto",
            json={
                "chat_id": user_db.chat_id,
                "photo": photo_id,
                "caption": msg,
                "parse_mode": "HTML",
                "reply_markup": keyword.bonus().to_dict(),
                "message_effect_id": "5046509860389126442",
            }
        )
        return state.BONUS


def get_user_boosts(chat_id, user_id):
    payload = {
        "chat_id": f'@{chat_id}',  # "@channelusername" yoki integer
        "user_id": user_id
    }
    API_URL = f"https://api.telegram.org/bot{settings.TOKEN}/getUserChatBoosts"
    response = requests.post(API_URL, json=payload)
    if response.ok:
        data = response.json()
        if data.get("ok"):
            return data["result"]['boosts']
    return False