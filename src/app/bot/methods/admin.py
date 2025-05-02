from ..tasks import send_advert_to_all
import time
from django.conf import settings
from telegram import Update, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from app.models import CustomUser, Channel, CustomUserAccount
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
import re
from telegram import MessageEntity
from html import escape as html_escape
from celery.result import AsyncResult
from core.celery import app

keyword = Keyboards()
state = States()
msg = MessageText()


def admin_base(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)
    # import subprocess
    # import os
    # import requests
    #
    # def compress_video(input_path, output_path="fixed_story.mp4"):
    #     print("🎞️ Videoni siqish boshlandi...")
    #     cmd = [
    #         "ffmpeg",
    #         "-i", input_path,
    #         "-vcodec", "libx264",
    #         "-acodec", "aac",
    #         "-preset", "veryfast",
    #         "-movflags", "+faststart",
    #         "-y", output_path
    #     ]
    #
    #     result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #
    #     if result.returncode == 0:
    #         print("✅ Siqish tugadi:", output_path)
    #         return output_path
    #     else:
    #         print("❌ ffmpeg xatolik:\n", result.stderr)
    #         return None
    #
    # def upload_to_telegra_ph(file_path):
    #     print("📤 Yuklanmoqda:", file_path)
    #     try:
    #         with open(file_path, 'rb') as f:
    #             response = requests.post(
    #                 'https://telegra.ph/upload',
    #                 files={'file': ('video.mp4', f, 'video/mp4')}
    #             )
    #
    #         print("📡 Javob kodi:", response.status_code)
    #         print("📨 Javob body:", response.text)
    #
    #         if response.status_code == 200:
    #             data = response.json()
    #             if isinstance(data, list) and "src" in data[0]:
    #                 return "https://telegra.ph" + data[0]['src']
    #     except Exception as e:
    #         print("❌ Exception:", str(e))
    #     return None
    #
    # input_file = "stories.mp4"
    # output_file = "fixed_story.mp4"
    #
    # if not os.path.exists(input_file):
    #         print(f"❗ Fayl topilmadi: {input_file}")
    #         exit()
    #
    # compressed = compress_video(input_file, output_file)
    # if compressed:
    #         url = upload_to_telegra_ph(compressed)
    #         if url:
    #             print("✅ Video yuklandi:", url)
    #         else:
    #             print("❌ Yuklashda xatolik")

    if admins.exists():
        _msg_ = "<b>Admin xush kelibsiz!</b>"
        update.message.reply_html(_msg_,
                                  reply_markup=keyword.admin_base())
        return state.ADMIN


def ads(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)
    if admins.exists():
        _msg_ = """
        Endi tugmani na‘muna bo'yicha joylang.
        <code>[CODER+https://t.me/khaydarovakbar]\n[TG bots+https://t.me/text_to_audiobot]</code>

        Agar tugma qo'yishni xohlamasangiz YUBORISH tugmasini bosing.
                """
        update.message.reply_html(_msg_,
                                  reply_markup=keyword.ads())
        return state.ADS


def get_ads(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)
    if admins.exists():
        update.message.reply_html(
            "<b>Reklama xabarini yuboring!</b>"
        )
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
        # if button_data:
        #     message = update.message
        #     chat_id = update.effective_chat.id
        #     message_id = context.bot_data['message_id']
        #     ads_text = context.bot_data['ads_text']
        #     task = send_advert_to_all.delay(
        #         chat_id=chat_id,
        #         message_id=message_id,
        #         button_data=button_data,
        #         ads_text=ads_text
        #     )
        #     context.bot_data[f'task_{message_id}'] = task.id
        #     message.reply_html(f"✅ Reklama fon rejimida yuborilmoqda. 🆔 <code>{task.id}</code>")
        #     return state.ADS_BUTTON
        context.chat_data['buttons'] = button_data
        update.message.reply_html(
            "Yaxshi! Tugmalarni qabul qildim endi Reklama xabarini yuboring..."
        )
        return state.ADS_BUTTON


def unparse_html_from_entities(text, entities):
    """
    Converts a Telegram message with entities into proper HTML-formatted string.
    Supports bold, italic, underline, code, pre, strikethrough, links.
    """

    if not entities:
        return html_escape(text or "")

    result = ""
    last_offset = 0
    open_tags = {
        'bold': '<b>',
        'italic': '<i>',
        'underline': '<u>',
        'strikethrough': '<s>',
        'code': '<code>',
        'pre': '<pre>',
    }
    close_tags = {
        'bold': '</b>',
        'italic': '</i>',
        'underline': '</u>',
        'strikethrough': '</s>',
        'code': '</code>',
        'pre': '</pre>',
    }

    for entity in sorted(entities, key=lambda e: e.offset):
        start = entity.offset
        end = entity.offset + entity.length

        # Qo'shilmagan oraliqni qo'shish
        result += html_escape(text[last_offset:start])

        entity_text = html_escape(text[start:end])

        if entity.type in open_tags:
            result += open_tags[entity.type] + entity_text + close_tags[entity.type]
        elif entity.type == 'text_link':
            result += f'<a href="{html_escape(entity.url)}">{entity_text}</a>'
        else:
            # noma'lum taglar
            result += entity_text

        last_offset = end

    result += html_escape(text[last_offset:])  # oxirgi qism

    return result


def received_advert(update, context):
    message = update.message
    chat_id = update.effective_chat.id
    button_data = context.chat_data.get('buttons', None)
    ads_text = None
    if message.entities:
        ads_text = unparse_html_from_entities(message.text, message.entities)
    else:
        from telegram.utils.helpers import escape
        ads_text = escape(message.text or "")
    message_id = update.message.message_id
    task = send_advert_to_all.delay(
        chat_id=chat_id,
        message_id=message_id,
        button_data=button_data,
        ads_text=ads_text
    )
    # task = send_advert_to_all.delay(
    #     ads_update=ads_update,
    #     button_data=button_data,
    # )
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
            # res.revoke(terminate=True, signal="SIGKILL")
            # update.message.reply_html("⛔ Task to‘xtatildi.")
            context.chat_data['task_id'] = task_id
            update.message.reply_html(
                "Tasdiqlash tugmasini bosing ✅",
                reply_markup=keyword.confirm(),
            )
            return state.CONFIRM
        else:
            update.message.reply_html("ℹ️ Bu task allaqachon yakunlangan yoki to‘xtatilgan.")

    except Exception as e:
        update.message.reply_text(f"⚠️ Xatolik: {str(e)}")


def confirm_kill_task(update, context):
    task_id = context.chat_data['task_id']

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
            # update.message.reply_html(
            #     "Tasdiqlash tugmasini bosing ✅",
            #     reply_markup=keyword.confirm(),
            # )
            # return state.CONFIRM
        else:
            update.message.reply_html("ℹ️ Bu task allaqachon yakunlangan yoki to‘xtatilgan.")

    except Exception as e:
        update.message.reply_text(f"⚠️ Xatolik: {str(e)}")


def get_user_id(update, context):
    update.message.reply_html(
        "<b>Izlamoqchi bo'lgan foydalanuvchi telegram id yoki telefon nomerini kiriting:</b>",
        reply_markup=keyword.back(),
    )
    return state.USER_ID


def get_user(update, context):
    user_msg = update.message.text.strip()

    is_phone = re.fullmatch(r"998\d{9}", user_msg)

    is_chat_id = re.fullmatch(r"\d{6,15}", user_msg)

    if is_phone:
        update.message.reply_text(f"📱 Siz telefon raqam kiritdingiz: {user_msg}")
        custom_user = CustomUser.objects.filter(phone_number=user_msg)
        if custom_user:
            user_db = custom_user.first()
            full_name = f"{user_db.first_name} {user_db.last_name}"  # yoki update.effective_chat.full_name

            msg = (
                f"🔍 Foydalanuvchi topildi!\n\n"
                f"👤 Foydalanuvchi: <a href='tg://user?id={user_db.chat_id}'>{full_name}</a>\n"
                f"🆔 Chat ID: <code>{user_db.chat_id}</code>\n"
                f"📲 Telefon nomer: +{user_db.phone_number}\n"
            )

            update.message.reply_html(msg)
        else:
            update.message.reply_text(
                "🚯 Siz kiritgan telefon nomer orqali bazada foydalanuvchi topilmadi")
            return state.USER_ID
    elif is_chat_id:
        update.message.reply_text(f"🆔 Siz Telegram chat ID kiritdingiz: {user_msg}")
        custom_user = CustomUser.objects.filter(chat_id=user_msg)

        if custom_user:
            user_db = custom_user.first()
            full_name = f"{user_db.first_name} {user_db.last_name}"  # yoki update.effective_chat.full_name

            msg = (
                f"🔍 Foydalanuvchi topildi!\n\n"
                f"👤 Foydalanuvchi: <a href='tg://user?id={user_db.chat_id}'>{full_name}</a>\n"
                f"🆔 Chat ID: <code>{user_db.chat_id}</code>\n"
                f"📲 Telefon nomer: +{user_db.phone_number}\n"
            )
            update.message.reply_html(msg)
        else:
            update.message.reply_text(
                "🚯 Siz kiritgan TELEGRAM ID orqali bazada foydalanuvchi topilmadi")
            return state.USER_ID
    else:
        update.message.reply_text(
            "❌ Noto‘g‘ri format. Iltimos, faqat 998 bilan boshlanuvchi telefon raqam yoki chat ID kiriting.")
        return state.USER_ID

    return state.USER_ID
