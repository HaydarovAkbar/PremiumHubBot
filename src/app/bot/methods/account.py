from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts, Group, CustomUserAccount, InvitedUser, Settings, SpendPrice, SpendPriceField, PromoCodes
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
import random

keyword = Keyboards()
state = States()
msg = MessageText()


def promo_code_generator():
    fields = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
        'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
        's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
        'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
    ]
    promo_code = ''.join(random.choice(fields) for _ in range(10))
    return promo_code


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
Sizning raqamingiz: +{user_db.phone_number}
</b>
"""
        promo_msg = ""
        my_promo_codes = PromoCodes.objects.filter(chat_id=update.effective_user.id, status=True)
        if my_promo_codes:
            promo_msg = "🔷 <b>Sizning promokodlaringiz:</b> 🔷\n"
        for my_promo_code in my_promo_codes:
            promo_msg += f"<code>{my_promo_code.name}</code>     -    Aktiv ✅\n"
        _msg += promo_msg
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
        query = update.callback_query
        account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id, )
        if query.data == 'back':
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.base())
            return state.START
        spend_field = SpendPriceField.objects.get(id=query.data)
        if account.current_price >= spend_field.price:
            context.chat_data['promo_code'] = query.data
            query.edit_message_text(
                f"""
<b>🎉 Siz ushbu taklifdan foydalana olasiz!</b>

Promokod olish tugmasini bosing,
hisobingizdan {spend_field.price} so'm yechiladi va
sizga promokod beriladi.
""",
                parse_mode=ParseMode.HTML,
                reply_markup=keyword.get_promo_code(),
            )
            return state.GET_PROMO_CODE
        else:
            query.answer()


def get_promo_code(update: Update, context: CallbackContext):
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
        account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id, )
        if query.data == 'back':
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.base())
            return state.START
        spend_field = SpendPriceField.objects.get(id=context.chat_data['promo_code'])
        user_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
        user_account.current_price -= spend_field.price
        user_account.save()
        promo_code = promo_code_generator()
        PromoCodes.objects.create(
            chat_id=update.effective_user.id,
            name=promo_code,
            status=True,
        )
        _msg_ = f"""
Sizga <b>{spend_field.name}</b> uchun promokod berildi

Sizning promokod 👉 <code>{promo_code}</code>
Narxi: <b>{spend_field.price} so'm </b>

Ushbu promokodni adminga yuboring.
Admin sizga taklif doirasidagi xizmatni faollashtiradi.
"""
        context.chat_data['promo_code'] = promo_code
        query.edit_message_text(
            _msg_,
            parse_mode=ParseMode.HTML,
            reply_markup=keyword.send_promo_code(),
        )
        return state.SEND_PROMO_CODE


def send_promo_code(update: Update, context: CallbackContext):
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
        account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id, )
        if query.data == 'back':
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.base())
            return state.START
        promo_code = context.chat_data['promo_code']
        spent_field = SpendPriceField.objects.get(id=context.chat_data['promo_code'])
        admins = CustomUser.objects.filter(is_admin=True)
        for admin in admins:
            try:
                adm_msg = (
                    f"🆕 Yangi promo kod ro'yxatdan o'tdi!\n\n"
                    f"🔹 Promo kod: <code>{promo_code}</code>\n"
                    f"🔹 Promo turi: <code>{spent_field.name}</code>\n"
                    f"🔹 Promo narxi: <code>{spent_field.price}</code>\n"
                    f"🔹 Foydalanuvchi: <a href='tg://user?id={user_db.chat_id}'>{update.effective_chat.full_name}</a>\n"
                    f"🔹 User ID: <code>{user_db.chat_id}</code>"
                )
                context.bot.send_message(chat_id=admin.chat_id,
                                         text=adm_msg,
                                         parse_mode='HTML',
                                         )
            except Exception:
                pass
        _msg_ = f"""
<b>✅ Promokod adminga muvafaqiyatli yuborildi!</b>

Tez orada xaridingiz tasdiqlanadi va amalga oshiriladi!!!
Iltimos biroz sabr qiling.
"""
        query.delete_message()
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text=_msg_,
                                 parse_mode=ParseMode.HTML,
                                 reply_markup=keyword.base())
        return state.START
