from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, CustomUserAccount, \
    InterestingBonus, InterestingBonusUser
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
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling)",
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
            _msg_ = f"""<b>O'z telegram ismingizga bizning nomimizni qo'ying va {interesting_bonus.fullname} so'm bonus oling.</b>
                    Ustiga bosib nusxalab olishingiz mumkin
                    
                    <code>🅿️ PremiumHub 📝</code>
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
Ustiga bosib nusxalab olishingiz mumkin

<code>Tg Premium 👇  https://t.me/HubPremiyumBot?start=758934089 📝</code>
                    """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_BIO


def check_interesting_bonus_nik(update: Update, context: CallbackContext):
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
        query = update.callback_query
        if query.data == 'back':
            _msg_ = "<b>Quyidagi qiziqarli vazifalarni bajarib bonuslar oling.</b>"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_bonus()
                                     )
            return state.INTERESTING_BONUS
        else:
            query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            interesting_bonus_user, _ = InterestingBonusUser.objects.get_or_create(
                chat_id=update.effective_user.id
            )
            user_full_name = update.effective_chat.full_name
            required_text = "PremiumHub"
            has_in_name = required_text.lower() in user_full_name.lower()
            if has_in_name:
                user_account = CustomUserAccount.objects.get(
                    chat_id=update.effective_user.id,
                )
                if interesting_bonus_user.fullname:
                    _msg_ = "<b>Siz allaqachon bu bonusni olgansiz!</b>"
                    query.delete_message()
                    context.bot.send_message(chat_id=update.effective_user.id,
                                             text=_msg_,
                                             parse_mode="HTML",
                                             reply_markup=keyword.interesting_bonus()
                                             )
                    return state.INTERESTING_BONUS
                bonus_amount = interesting_bonus.fullname
                user_account.current_price += bonus_amount
                user_account.total_price += bonus_amount
                user_account.save()
                interesting_bonus_user.fullname = True
                interesting_bonus_user.save()
                _msg_ = f"""✅ Tabriklaymiz! Siz {bonus_amount} so'm bonus qo'lga kiritdingiz."""
                context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=_msg_,
                    parse_mode="HTML"
                )
                return state.INTERESTING_BONUS_NIK
            _msg_ = f"""
❗️ <b>Kechirasiz tekshirish natijasida sizda talabga javob beradigan nikname aniqlanmadi
O'z telegram Ismingizni ingizga bizning nomimizni qo'ying va {interesting_bonus.bio} so'm bonus oling.</b>

Ustiga bosib nusxalab olishingiz mumkin

<code>Tg Premium 👇  https://t.me/HubPremiyumBot?start=758934089 📝</code>
                    """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_NIK


def check_interesting_bonus_bio(update: Update, context: CallbackContext):
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
        query = update.callback_query
        if query.data == 'back':
            _msg_ = "<b>Quyidagi qiziqarli vazifalarni bajarib bonuslar oling.</b>"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_bonus()
                                     )
            return state.INTERESTING_BONUS
        else:
            query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            interesting_bonus_user, _ = InterestingBonusUser.objects.get_or_create(
                chat_id=update.effective_user.id
            )
            user_bio = update.effective_chat.bio or "" if hasattr(update.effective_chat, 'bio') else ""
            required_text = "Tg Premium 👇 https://t.me/HubPremiyumBot?start=758934089"
            has_in_name = required_text.lower() in user_bio.lower()
            if has_in_name:
                user_account = CustomUserAccount.objects.get(
                    chat_id=update.effective_user.id,
                )
                if interesting_bonus_user.bio:
                    _msg_ = "<b>Siz allaqachon bu bonusni olgansiz!</b>"
                    query.delete_message()
                    context.bot.send_message(chat_id=update.effective_user.id,
                                             text=_msg_,
                                             parse_mode="HTML",
                                             reply_markup=keyword.interesting_bonus()
                                             )
                    return state.INTERESTING_BONUS
                bonus_amount = interesting_bonus.bio
                user_account.current_price += bonus_amount
                user_account.total_price += bonus_amount
                user_account.save()
                interesting_bonus_user.bio = True
                interesting_bonus_user.save()
                _msg_ = f"""✅ Tabriklaymiz! Siz {bonus_amount} so'm bonus qo'lga kiritdingiz."""
                context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=_msg_,
                    parse_mode="HTML"
                )
                return state.INTERESTING_BONUS_BIO
            _msg_ = f"""<b>
❗️ Kechirasiz tekshirish natijasida sizda talabga javob beradigan nikname aniqlanmadi
O'z telegram BIO ingizga bizning nomimizni qo'ying va {interesting_bonus.bio} so'm bonus oling.</b>

Ustiga bosib nusxalab olishingiz mumkin


<code>Tg Premium 👇  https://t.me/HubPremiyumBot?start=758934089 📝</code>
                        """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_BIO
