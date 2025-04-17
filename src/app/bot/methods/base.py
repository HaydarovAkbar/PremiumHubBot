import time
from django.conf import settings
from telegram import Update
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()


def check_channel(update: Update, context: CallbackContext):
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


def add_to_channel(update: Update, context: CallbackContext):
    query = update.callback_query
    channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for ch in channel:
        try:
            a = context.bot.get_chat_member(chat_id=ch.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(ch)
        except Exception as e:
            print(e)

    query.delete_message()
    time.sleep(0.1)
    if left_channel:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    return start(update, context)


def start(update: Update, context: CallbackContext):
    all_channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for channel in all_channel:
        try:
            a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(channel)
        except Exception as e:
            print("Error:", e)
    if left_channel:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botni ishga tushirish uchun quyidagi kanallarga obuna bo’ling va “♻️ Tekshirish” tugmasini bosing",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user, _ = CustomUser.objects.get_or_create(chat_id=update.effective_user.id, defaults={
        'username': update.effective_user.username,
        'first_name': update.effective_user.first_name,
        'last_name': update.effective_user.last_name,
        'is_active': False,
    })
    if user.is_blocked:
        update.message.reply_text(
            "Siz botdan ko’p marta ro’yxatdan o’tganingiz uchun bot sizni bloklagan, agar buni xato deb hisoblasangiz, @hup_support ga murojaat qiling"
        )
        return state.START
    if not _:
        if not user.phone_number:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Botdan to’liq foydalanish uchun “Telefon raqamni yuborish” tugmasini bosing",
                                     parse_mode='HTML',
                                     reply_markup=keyword.phone_number(),
                                     )
            return state.PHONE
        if not user.is_active:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="""🔁Botimiz yangilangani va xavfsizlikni oshirish munosabati bilan quyidagi havola orqali ro’yxatdan o’ting va botni ishlatishda davom eting
""",
                                     parse_mode='HTML',
                                     reply_markup=keyword.signup(settings.SIGNUP_URL))
            return state.SIGNUP
        context.bot.send_message(chat_id=update.effective_user.id, text=msg.BASE_MSG,
                                 parse_mode='HTML',
                                 reply_markup=keyword.base())
        return state.START

    context.bot.send_message(chat_id=update.effective_user.id,
                             text="Botdan to’liq foydalanish uchun “Telefon raqamni yuborish” tugmasini bosing",
                             parse_mode='HTML',
                             reply_markup=keyword.phone_number(),
                             )
    return state.PHONE


def get_contact(update: Update, context: CallbackContext):
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
        context.bot.send_message(chat_id=update.effective_user.id, text="msg_text.add_to_channel.get(user_lang)",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user = CustomUser.objects.get(chat_id=update.effective_user.id)
    user.phone_number = update.message.contact.phone_number
    user.save()
    if not user.is_active:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="""🔁Botimiz yangilangani va xavfsizlikni oshirish munosabati bilan quyidagi havola orqali ro’yxatdan o’ting va botni ishlatishda davom eting
    """,
                                 parse_mode='HTML',
                                 reply_markup=keyword.signup(settings.SIGNUP_URL))
        return state.SIGNUP
    update.message.reply_html(msg.BASE_MSG, reply_markup=keyword.base())
    return state.START


def get_contact_text(update: Update, context: CallbackContext):
    user_msg = update.message.text
    user_db = CustomUser.objects.filter(chat_id=update.effective_user.id)
    if user_msg.startswith('+998') and len(user_msg) == 13:
        user_msg = user_msg
    elif user_msg.startswith('998') and len(user_msg) == 12:
        user_msg = '+' + user_msg
    else:
        update.message.reply_html("msg_text.phone_number_error.get(user_lang)", reply_markup=keyword.phone_number())
    user_db.phone_number = user_msg
    user_db.save()
    if not user_db.is_active:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="""🔁Botimiz yangilangani va xavfsizlikni oshirish munosabati bilan quyidagi havola orqali ro’yxatdan o’ting va botni ishlatishda davom eting
    """,
                                 parse_mode='HTML',
                                 reply_markup=keyword.signup(settings.SIGNUP_URL))
        return state.SIGNUP
    update.message.reply_html(msg.BASE_MSG, reply_markup=keyword.base())
    return state.START
