from ..task import send_advert_to_all
import time
from django.conf import settings
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, CustomUserAccount
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()


def admin_base(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)
    if admins.exists():
        _msg_ = "<b>Admin xush kelibsiz!</b>"
        update.message.reply_html(_msg_,
                                  reply_markup=keyword.admin_base())
        return state.ADMIN


def ads(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)
    if admins.exists():
        _msg_ = "<b>Reklama xabarini kiriting</b>"
        update.message.reply_html(_msg_,
                                  reply_markup=keyword.back())
        return state.ADS


def get_ads(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)
    if admins.exists():
        msg_id = update.message.message_id
        context.bot_data['message_id'] = msg_id
        _msg_ = """
Yaxshi, post qabul qildim!
Endi tugmani na‘muna bo'yicha joylang.
<code>[CODER+https://t.me/khaydarovakbar]\n[TG bots+https://t.me/text_to_audiobot]</code>

Agar tugma qo'yishni xohlamasangiz YUBORISH tugmasini bosing.
        """
        update.message.reply_html(_msg_, reply_markup=keyword.ads())
        return state.ADS_BUTTON


def parse_button(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)
    if admins.exists():
        button_txt = update.message.text


def received_advert(update, context):
    message = update.message
    chat_id = update.effective_chat.id
    message_id = context.bot_data['message_id']

    task = send_advert_to_all.delay(chat_id, message_id)  # Celery taskni fon ishga beradi
    print(task.status)
    context.bot_data[f'task_{message_id}'] = task.id
    message.reply_text(f"✅ Reklama fon rejimida yuborilmoqda. {task.id}")
    return state.ADS_BUTTON
