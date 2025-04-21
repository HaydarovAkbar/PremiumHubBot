from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts, Group, CustomUserAccount, InvitedUser, Settings, SpendPrice, SpendPriceField
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()


def my_account(update: Update, context: CallbackContext):
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
        account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id,
                                                             defaults={
                                                                 'current_price': 0.0,
                                                                 'total_price': 0.0,
                                                             }
                                                             )
        group_added_count = InvitedUser.objects.filter(inviter_chat_id=update.effective_user.id).count()
        _msg = f"""<b>
{update.effective_chat.full_name} sizning balansingiz: {account.current_price} soʻm
Taklif qilgan do‘stlaringiz: {user_db.invited_count} ta
Premium doʻstlar: {user_db.premium_count} ta 
Guruhimizga taklif qilgan do'stlaringiz: {group_added_count} ta 
Sizning raqamingiz: {user_db.phone_number}
</b>
"""
        update.message.reply_html(
            _msg,
            reply_markup=keyword.my_account(),
        )
        return state.START


def spend(update: Update, context: CallbackContext):
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

        account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id,
                                                             )
        settings_bot = Settings.objects.filter(is_active=True).last()
        if account.current_price >= settings_bot.spend_price:
            last_spend_price = SpendPrice.objects.filter(is_active=True).last()
            if last_spend_price:
                fields = SpendPriceField.objects.filter(spend_price=last_spend_price)
                update.callback_query.delete_message()
                context.bot.send_message(chat_id=update.effective_user.id, text=last_spend_price.text,
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=keyword.spend_fields(fields, account.current_price),
                                         )
                return state.MY_ACCOUNT
            update.callback_query.answer(
                f"Kechirasiz xizmat hali to'liq ishga tushmagan !",
            )
        else:
            update.callback_query.answer(
                f"Bu xizmatdan foydalanish uchun hisobingizda {settings_bot.spend_price - account.current_price} so'm yetishmayapti!",
            )
        return state.START


def spend_field(update: Update, context: CallbackContext):
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

        account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id,
                                                             )
        settings_bot = Settings.objects.filter(is_active=True).last()
        if account.current_price >= settings_bot.spend_price:
            last_spend_price = SpendPrice.objects.filter(is_active=True).last()
            if last_spend_price:
                fields = SpendPriceField.objects.filter(spend_price=last_spend_price)
                update.callback_query.delete_message()
                context.bot.send_message(chat_id=update.effective_user.id, text=last_spend_price.text,
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=keyword.spend_fields(fields, account.current_price),
                                         )
                return state.MY_ACCOUNT
            update.callback_query.answer(
                f"Kechirasiz xizmat hali to'liq ishga tushmagan !",
            )
        else:
            update.callback_query.answer(
                f"Bu xizmatdan foydalanish uchun hisobingizda {settings_bot.spend_price - account.current_price} so'm yetishmayapti!",
            )
        return state.START
