from ..tasks import send_advert_to_all
import time
from django.conf import settings
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from app.models import CustomUser, Channel, CustomUserAccount
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

from celery.result import AsyncResult
from core.celery import app

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
        try:
            text = update.message.text_html or "📢"
        except Exception:
            from telegram.utils.helpers import escape
            text = escape(update.message.text)
        context.bot_data['ads_text'] = text
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
        import re

        def parse_buttons_from_text(text):
            pattern = r'\[(.+?)\+(.+?)\]'
            matches = re.findall(pattern, text)

            buttons = []
            for label, url in matches:
                buttons.append({"text": label.strip(), "url": url.strip()})

            return buttons

        button_data = parse_buttons_from_text(update.message.text)
        if button_data:
            message = update.message
            chat_id = update.effective_chat.id
            message_id = context.bot_data['message_id']
            ads_text = context.bot_data['ads_text']
            task = send_advert_to_all.delay(
                chat_id=chat_id,
                message_id=message_id,
                button_data=button_data,
                ads_text=ads_text
            )
            context.bot_data[f'task_{message_id}'] = task.id
            message.reply_html(f"✅ Reklama fon rejimida yuborilmoqda. 🆔 <code>{task.id}</code>")
            return state.ADS_BUTTON


def received_advert(update, context):
    message = update.message
    chat_id = update.effective_chat.id
    message_id = context.bot_data['message_id']
    task = send_advert_to_all.delay(
        chat_id=chat_id,
        message_id=message_id,
        button_data=None,
        ads_text=None)
    context.bot_data[f'task_{message_id}'] = task.id
    message.reply_html(f"✅ Reklama fon rejimida yuborilmoqda. 🆔 <code>{task.id}</code>")
    return state.ADS_BUTTON


def kill_task(update, context):
    get_task_id = "<b>Task ID kiriting:</b> 🆔 ?"
    update.message.reply_html(
        get_task_id,
        reply_markup=keyword.back(),
    )
    return state.KILL_TASK


def get_kill_id(update, context):
    task_id = update.message.text.strip()

    STATUS = {
        'PENDING': "⏱️ KUTILMOQDA",
        'STARTED': "⚙️ ISH BOSHLANGAN",
        'SUCCESS': "✅ BAJARILDI",
        'FAILURE': "❌ XATO YUZ BERDI",
        'REVOKED': "⛔ TO‘XTATILGAN",
        'RETRY': "🔁 QAYTA URINILMOQDA"
    }

    try:
        res = AsyncResult(task_id, app=app)
        state = res.state

        msg = f"<b>Task status:</b> {STATUS.get(state, state)}\n🆔 <code>{task_id}</code>"
        update.message.reply_html(msg)

        if state not in ["SUCCESS", "FAILURE", "REVOKED"]:
            res.revoke(terminate=True, signal="SIGKILL")
            update.message.reply_html("⛔ Task to‘xtatildi.")
        else:
            update.message.reply_html("ℹ️ Bu task allaqachon yakunlangan yoki to‘xtatilgan.")

    except Exception as e:
        update.message.reply_text(f"⚠️ Xatolik: {str(e)}")
