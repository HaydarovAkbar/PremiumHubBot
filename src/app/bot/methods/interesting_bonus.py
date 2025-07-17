from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, CustomUserAccount, \
    InterestingBonus, InterestingBonusUser, TopUser
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()


def get_interesting_bonus_base(update: Update, context: CallbackContext):
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
        # context.bot.send_message(chat_id=update.effective_user.id,
        #                          text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling)",
        #                          reply_markup=keyword.channels(left_channel))
        context.bot.send_photo(chat_id=update.effective_user.id,
                               photo='AgACAgIAAxkBAAEaMCdoeJzgVCgsP05l79z72EpYtLSnfAACB_oxG14bwUsodGhV1zrgcAEAAwIAA3kAAzYE',
                               caption="Botni ishga tushirish uchun quyidagi kanallarga obuna bo’ling va “♻️ Tekshirish” tugmasini bosing",
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
        elif query.data == 'nik':
            query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            _msg_ = f"""
<b>O'z telegram ismingizga bizning nomimizni qo'ying va {interesting_bonus.fullname} so'm bonus oling.</b>
<i>Ustiga bosib nusxalab olishingiz mumkin</i>
                    
<code>🅿️ PremiumHub</code> 📝
                    """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_NIK
        else:
            query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            _msg_ = f"""
<b>O'z telegram BIO ingizga bizning nomimizni qo'ying va {interesting_bonus.bio} so'm bonus oling.</b>
<i>Ustiga bosib nusxalab olishingiz mumkin</i>

<code>Telegram Premium 👇  https://t.me/HubPremiyumBot?start={update.effective_user.id}</code> 📝
                    """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_BIO
