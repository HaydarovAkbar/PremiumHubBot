from decouple import TRUE_VALUES
from django.db.models.functions import Replace
from decimal import Decimal
from .. import keyboards
from ..tasks import send_advert_to_all
import requests
from django.conf import settings
from telegram import Update, InlineKeyboardMarkup, ParseMode, ReplyKeyboardRemove, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from app.models import CustomUser, Channel, CustomUserAccount, PromoCodes, StoryBonusAccounts, InvitedUser, \
    InterestingBonusUser, DailyBonus, TopUser, CustomPromoCode
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
import re
from telegram import MessageEntity
from html import escape as html_escape
from celery.result import AsyncResult
from core.celery import app
import redis
from ...models import InterestingBonus

keyword = Keyboards()
state = States()
msg = MessageText()
API_URL = f"https://api.telegram.org/bot{settings.TOKEN}/"


def admin_base(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)

    if admins.exists():
        stiker_id = "CAACAgIAAxkBAAEDsX1h4zDsLzkJZ5FxIQ3t4gStVwf0mAACQAEAAladvQps6VtALEnWJSME"

        adm_url = f"{settings.HOST}/admin/"
        stat_url = f"{settings.HOST}/stats/"

        if update.effective_chat.id == 749750897 or update.effective_chat.id == 758934089:  # Akbar's chat_id or update.effective_chat.id == 758934089 6847181437
            update.message.reply_sticker(
                sticker=stiker_id,
                reply_markup=keyword.admin_base()
            )
            update.message.reply_html(
                "<b>Web adminkaga o'tish</b> \n\n/start - Bosh sahifasi\n/admin - Admin sahifasi\n/promo - Promo kod haqida ma'lumot olish (/promo xSfdXdf)\n/promocodes - Promo kodlar\n/stories - Bonus bajarganlar",
                reply_markup=keyword.adm_url(adm_url, stat_url),
            )
        else:
            update.message.reply_sticker(
                sticker=stiker_id,
                reply_markup=keyword.admin_base2()
            )
            update.message.reply_html(
                "<b>Web adminkaga o'tish</b> \n\n/start - Bosh sahifasi\n/admin - Admin sahifasi\n/promo - Promo kod haqida ma'lumot olish (/promo xSfdXdf)\n/promocodes - Promo kodlar\n/stories - Bonus bajarganlar",
                reply_markup=keyword.adm_url2(adm_url, stat_url),
            )
        return state.ADMIN


def detect_message_method(message):
    if message.forward_from or message.forward_sender_name or message.forward_from_chat or message.forward_signature:
        return 'forwardMessage'
    elif message.reply_markup or message.sticker:
        return 'copyMessage'
    elif message.text and message.entities:
        return 'sendMessage'
    else:
        return 'copyMessage'


def build_payload(message, user_chat_id, method):
    if method == 'sendMessage':
        return {
            "chat_id": user_chat_id,
            "text": message.text,
            "entities": [e.to_dict() for e in message.entities] if message.entities else None
        }
    elif method == 'forwardMessage':
        return {
            "chat_id": user_chat_id,
            "from_chat_id": message.chat_id,
            "message_id": message.message_id
        }
    elif method == 'copyMessage':
        return {
            "chat_id": user_chat_id,
            "from_chat_id": message.chat_id,
            "message_id": message.message_id,
            "reply_markup": message.reply_markup.to_dict() if message.reply_markup else None
        }


def ads(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.message.chat_id)
    if admins.exists():
        msg = (
            "Endi tugmani na‘muna bo'yicha joylang.\n"
            "<code>[CODER+https://t.me/khaydarovakbar]\n[TG bots+https://t.me/text_to_audiobot]</code>\n\n"
            "Agar tugma qo'yishni xohlamasangiz Davom etish tugmasini bosing."
        )
        update.message.reply_html(msg, reply_markup=keyword.ads())
        return state.ADS


def get_ads(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        update.message.reply_html("<b>Reklama xabarini yuboring!</b>", reply_markup=keyword.back())
        return state.ADS_BUTTON


def parse_buttons_from_text(text):
    pattern = r'\[(.+?)\+(.+?)\]'
    matches = re.findall(pattern, text)
    return [{"text": label.strip(), "url": url.strip()} for label, url in matches]


def parse_button(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        button_data = parse_buttons_from_text(update.message.text)
        context.chat_data['buttons'] = button_data
        update.message.reply_html("Yaxshi! Tugmalarni qabul qildim, endi reklama xabarini yuboring...")
        return state.ADS_BUTTON


def received_advert(update: Update, context: CallbackContext):
    if not update.effective_chat.id in [749750897, 758934089, 6847181437]:
        update.message.reply_text("Sizda bu amallarni bajarish huquqi yo'q!")
        return ConversationHandler.END
    message = update.message
    chat_id = update.effective_chat.id
    button_data = context.chat_data.get('buttons')
    method = detect_message_method(message)

    # 🔒 Saqlab qo‘yamiz
    context.chat_data['ads_text'] = message.text
    context.chat_data['method'] = method
    context.chat_data['message_id'] = message.message_id
    context.chat_data['buttons'] = button_data

    # 1. Info matn
    context.bot.send_message(
        chat_id=chat_id,
        text="📢 <b>Reklama xabaringiz quyidagicha ko‘rinadi:</b>",
        parse_mode="HTML"
    )

    if method == 'forwardMessage':
        requests.post(f"{API_URL}forwardMessage", json={
            "chat_id": chat_id,
            "from_chat_id": message.chat_id,
            "message_id": message.message_id
        })

    elif method == 'copyMessage':
        copy_payload = {
            "chat_id": chat_id,
            "from_chat_id": message.chat_id,
            "message_id": message.message_id
        }
        if button_data:
            copy_payload["reply_markup"] = {
                "inline_keyboard": [[{"text": b["text"], "url": b["url"]}] for b in button_data]
            }
        requests.post(f"{API_URL}copyMessage", json=copy_payload)
    else:
        copy_payload = {
            "chat_id": chat_id,
            "from_chat_id": message.chat_id,
            "message_id": message.message_id
        }
        if button_data:
            copy_payload["reply_markup"] = {
                "inline_keyboard": [[{"text": b["text"], "url": b["url"]}] for b in button_data]
            }
        requests.post(f"{API_URL}copyMessage", json=copy_payload)

    # 3. Tasdiqlash tugmalari
    confirm_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_ad"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_ad")
        ]
    ])

    context.bot.send_message(
        chat_id=chat_id,
        text="Tasdiqlaysizmi?",
        reply_markup=confirm_markup
    )

    return state.ADS_BUTTON


def confirm_or_cancel_ad(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        update.message.reply_text("Sizda bu amallarni bajarish huquqi yo'q!")
        return ConversationHandler.END
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat.id
    data = query.data

    if data == "cancel_ad":
        query.edit_message_text("❌ Reklama bekor qilindi.")
        context.chat_data.clear()
        return state.ADS

    elif data == "confirm_ad":
        # 🔃 Ma’lumotlarni qayta chaqiramiz
        ads_text = context.chat_data.get('ads_text')
        method = context.chat_data.get('method')
        message_id = context.chat_data.get('message_id')
        button_data = context.chat_data.get('buttons')

        task = send_advert_to_all.apply_async(
            args=[chat_id, message_id],
            kwargs={
                "method": method,
                "button_data": button_data,
                "ads_text": ads_text
            }
        )

        query.delete_message()
        context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Reklama yuborilmoqda. 🆔 <code>{task.id}</code>",
            parse_mode="HTML",
            reply_markup=keyword.admin_base()
        )

        context.bot_data[f'task_{message_id}'] = task.id
        context.chat_data.clear()
        return state.ADS


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

            # Redis’dan task metadata'ni o‘chirish
            r = redis.StrictRedis(host='localhost', port=6379, db=0)  # kerak bo‘lsa host/portni moslang
            deleted = r.delete(f'celery-task-meta-{task_id}')
            if deleted:
                update.message.reply_html("🧹 Redis task metadata ham tozalandi.")
            else:
                update.message.reply_html("⚠️ Redis’da task metadata topilmadi yoki allaqachon o‘chirilgan.")
        else:
            update.message.reply_html("ℹ️ Bu task allaqachon yakunlangan yoki to‘xtatilgan.")

    except Exception as e:
        update.message.reply_text(f"⚠️ Xatolik: {str(e)}")


def get_user_id(update, context):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if not admins.exists():
        return ConversationHandler.END
    update.message.reply_html(
        "<b>Izlamoqchi bo'lgan foydalanuvchi telegram id yoki telefon nomerini kiriting:</b>",
        # reply_markup=keyword.back(),
    )
    return state.USER_ID


def get_user(update, context):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if not admins.exists():
        return ConversationHandler.END
    user_msg = update.message.text.strip()

    is_phone = re.fullmatch(r"998\d{9}", user_msg)

    is_chat_id = re.fullmatch(r"\d{6,15}", user_msg)

    if is_phone:
        update.message.reply_text(f"📱 Siz telefon raqam kiritdingiz: {user_msg}")
        custom_user = CustomUser.objects.filter(phone_number=user_msg)
    elif is_chat_id:
        update.message.reply_text(f"🆔 Siz Telegram chat ID kiritdingiz: {user_msg}")
        custom_user = CustomUser.objects.filter(chat_id=user_msg)
    else:
        update.message.reply_text(
            "❌ Noto‘g‘ri format. Iltimos, faqat 998 bilan boshlanuvchi telefon raqam yoki chat ID kiriting.")
        return state.USER_ID
    if custom_user:
        user_db = custom_user.first()
        full_name = f"{user_db.first_name} {user_db.last_name}"  # yoki update.effective_chat.full_name
        if user_db.is_active:
            status = "Aktive ✅"
        if user_db.is_blocked:
            status = "Bloklangan 🔒"
        if user_db.is_admin:
            status = "Admin 👮‍♀️"
        else:
            status = "Passive"
        custom_user_account, __ = CustomUserAccount.objects.get_or_create(chat_id=user_db.chat_id)
        context.chat_data['chat_id'] = user_db.chat_id
        story_ = StoryBonusAccounts.objects.filter(chat_id=user_db.chat_id)
        if story_:
            story_ = story_.first()
        else:
            story_ = True

        boost = DailyBonus.objects.filter(chat_id=user_db.chat_id)
        if boost:
            boost = boost.first()
        else:
            boost = True
        interesting_b = InterestingBonusUser.objects.filter(chat_id=user_db.chat_id)
        if interesting_b:
            interesting_b = interesting_b.first()
            bio = True if interesting_b.bio else False
            nik = True if interesting_b.fullname else False
        else:
            bio = False
            nik = False
        invited_group_count = InvitedUser.objects.filter(inviter_chat_id=user_db.chat_id).count()

        msg = (
            f"🔍 Foydalanuvchi topildi!\n\n"
            f"👤 Foydalanuvchi: <a href='tg://user?id={user_db.chat_id}'>{full_name}</a>\n"
            f"👤 Username: @{user_db.username}\n"
            f"♻️ Holati: {status}\n"
            f"🆔 Chat ID: <code>{user_db.chat_id}</code>\n"
            f"📲 Telefon nomer: +{user_db.phone_number}\n"
            f"💰 Hozirgi balanse: {custom_user_account.current_price} 💎 \n\n"
            f"🗒 Vazifalar ro'yxati:\n"
            f"👤 Taklif qilganlar soni {user_db.invited_count}\n"
            f"👤 Guruhga qo'shganlar soni {invited_group_count}\n"
            f"🔹 BIO BONUS {bio}\n🔹 NIKNAME {nik}\n"
            f"💫 Stories bonus: {True if story_ else False}\n"
            f"💫 Reward bonus: {True if boost else False}\n"
        )
        update.message.reply_html(msg, reply_markup=keyword.adm_user_profile())
        return state.USER_PROFILE
    else:
        update.message.reply_text(
            "🚯 Siz kiritgan TELEGRAM ID orqali bazada foydalanuvchi topilmadi")

    return state.USER_ID


def info_promo(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        promo = context.args[0] if len(context.args) == 1 else False
        if promo:
            get_db_promo = PromoCodes.objects.filter(name=promo, status=True)
            if get_db_promo.exists():
                promo_code = get_db_promo.first()
                promo_user = CustomUser.objects.get(chat_id=promo_code.chat_id)
                fullname = f"{promo_user.first_name if promo_user.first_name else '-'} {promo_user.last_name if promo_user.last_name else '-'}"
                mention = f"<a href='tg://user?id={promo_user.chat_id}'>{fullname}</a>"
                status = "Aktive ✅" if promo_code.status else "Passive ☑️"
                update.message.reply_html(
                    f"""
🤖 <b>Promo kod haqida to'liq ma'lumot:</b>

🆔 PromoKOD: {promo_code.name}
📛 PromoNAME: <code>{promo_code.reward}</code>
📅 PromoDATE: <code>{promo_code.created_at.date()}</code>
📊 PromoSTATUS: <code>{status}</code>

👨‍🦲 PromoUSER: {mention}
🆔 PromoUSER_ID: <code>{promo_user.chat_id}</code>
☎️ PromoUSER_PHONE: +{promo_user.phone_number}
""",
                    reply_markup=keyword.passive()
                )
                context.chat_data["promo_code"] = promo
                return state.PASSIVE
            else:
                update.message.reply_text(
                    "Bazadan bu promokod haqida ma'lumot topilmadi!",
                )
        else:
            update.message.reply_text(
                "Promo kod kiritmadingiz!"
            )


def get_all_promo_codes(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        promo_codes = PromoCodes.objects.filter(status=True).order_by('created_at')[:100]
        if promo_codes.exists():
            msg = f"✅ <b>Oxirgi 100 ta aktiv promokodlar</b>\n\n"
            counter = 1
            for promo_code in promo_codes:
                msg += f"{counter}). <code>{promo_code.name}</code> - {promo_code.created_at.date()} - {promo_code.reward}\n"
                counter += 1

            update.message.reply_html(msg)
        else:
            update.message.reply_html(
                "Hozirda aktiv promokodlar mavjud emas!"
            )


def passive(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if not admins.exists():
        return ConversationHandler.END
    callback_query = update.callback_query
    promo = context.chat_data["promo_code"]
    promo_db = PromoCodes.objects.get(name=promo)
    promo_db.status = False if promo_db.status else True
    promo_db.save()
    callback_query.edit_message_text("Passive qilindi ✅")
    return state.ADMIN


def user_profile(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if not admins.exists():
        update.message.reply_text("Sizda bu amallarni bajarish huquqi yo'q!")
        return ConversationHandler.END
    callback_query = update.callback_query
    user_db = CustomUser.objects.get(chat_id=context.chat_data['chat_id'])

    if callback_query.data == "is_ban":
        user_db.is_blocked = True
        user_db.is_active = False
        user_db.is_admin = False
        user_db.save()
        callback_query.answer("Foydalanuvchi blok qilindi!", show_alert=True)
    elif callback_query.data == "no_ban":
        user_db.is_blocked = False
        user_db.is_active = True
        user_db.save()
        callback_query.answer("Foydalanuvchi blokdan ochildi!", show_alert=True)
    elif callback_query.data == "get_balance":
        callback_query.edit_message_text(
            "Foydalanuvchidan qancha miqdorda pul yechmoqchisiz yuboring (M: 5000)"
        )
        return state.GET_BALANCE
    elif callback_query.data == "push_balance":
        callback_query.edit_message_text(
            "Foydalanuvchiga qancha miqdorda pul kiritmoqchisiz yuboring (M: 5000)"
        )
        return state.PUSH_BALANCE
    elif callback_query.data == "send_msg":
        callback_query.edit_message_text(
            "Foydalanuvchiga qanday xabar yubormoqchisiz yuboring!"
        )
        return state.SEND_MSG
    elif callback_query.data == "referral":
        user_referrals = CustomUser.objects.filter(referral=user_db.chat_id)
        if user_referrals.exists():
            msg = "<b>Foydalanuvchi referral qilgan akkountlar:</b>\n\nN)   Familiya-Ism    Status\n"
            counter = 1
            for user_referral in user_referrals:
                fullname = user_referral.first_name if user_referral.first_name else '-' + " " + user_referral.last_name if user_referral.last_name else '-'
                minio = f"<a href='tg://user?id={user_referral.chat_id}'>{fullname}</a>"
                msg += f"{counter}). {minio} - {user_referral.is_active}\n"
                counter += 1
            context.bot.send_message(chat_id=callback_query.message.chat_id,
                                     text=msg,
                                     parse_mode=ParseMode.HTML)
        else:
            callback_query.answer(
                "Foydalanuvchi refferal qilmagan hali!", show_alert=True
            )


def get_balance(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if not admins.exists():
        update.message.reply_text("Sizda bu amallarni bajarish huquqi yo'q!")
        return ConversationHandler.END
    get_price = update.message.text
    user_profile = CustomUser.objects.get(chat_id=context.chat_data['chat_id'])
    user_account = CustomUserAccount.objects.get(chat_id=context.chat_data['chat_id'])
    if user_account.current_price >= Decimal(get_price):
        user_account.current_price -= Decimal(get_price)
        user_account.save()
        try:
            fullname = user_profile.first_name if user_profile.first_name else '-' + " " + user_profile.last_name if user_profile.last_name else '-'
            minio = f"<a href='tg://user?id={user_profile.chat_id}'>{fullname}</a>"
            adm_msg = (
                f"<b>🆕 Foydalanuvchiga pul olindi!\n\n</b>"
                f"🛑 hisobidan olind\n"
                f"🔹 FamiliyaIsm: {minio}\n"
                f"🔹 Kamayish narxi: <code>{float(get_price)}</code>\n"
                f"🔹 User ID: <code>{user_profile.chat_id}</code>\n"
                f"📅 DATE: {user_profile.created_at}\n"
            )
            context.bot.send_message(chat_id=-1002275382452,
                                     text=adm_msg,
                                     parse_mode='HTML',
                                     )
        except Exception as e:
            context.bot.send_message(chat_id=758934089,
                                     text=str(e),
                                     parse_mode='HTML',
                                     )
        update.message.reply_text(
            f"Balanse kamaytirildi!\nFoydalanuvchini hozirgi balanse: {user_account.current_price} so'm",
            reply_markup=keyword.admin_base()
        )
        return state.ADMIN
    else:
        update.message.reply_text(
            "Siz kiritgan miqdor foydalanuvchi miqdoridan ancha yuqori ekan!"
        )


def push_balance(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if not admins.exists():
        update.message.reply_text("Sizda bu amallarni bajarish huquqi yo'q!")
        return ConversationHandler.END
    get_price = update.message.text
    user_account = CustomUserAccount.objects.get(chat_id=context.chat_data['chat_id'])
    user_account.current_price += Decimal(get_price)
    user_account.total_price += Decimal(get_price)
    user_account.save()
    top_user, a = TopUser.objects.get_or_create(
        chat_id=update.effective_user.id,
        defaults={
            'fullname': update.effective_user.full_name,
        }
    )
    top_user.balance += Decimal(get_price)
    top_user.weekly_earned += Decimal(get_price)
    # top_user.monthly_earned += int(get_price)
    top_user.save()
    user_profile = CustomUser.objects.get(chat_id=context.chat_data['chat_id'])
    try:
        fullname = user_profile.first_name if user_profile.first_name else '-' + " " + user_profile.last_name if user_profile.last_name else '-'
        minio = f"<a href='tg://user?id={user_profile.chat_id}'>{fullname}</a>"
        adm_msg = (
            f"<b>🆕 Foydalanuvchiga pul qo'shildi!\n\n</b>"
            f"✅ hisobiga qoshildi\n"
            f"🔹 FamiliyaIsm: {minio}\n"
            f"🔹 Kamayish narxi: <code>{float(get_price)}</code>\n"
            f"🔹 User ID: <code>{user_profile.chat_id}</code>\n"
            f"📅 DATE: {user_profile.created_at}\n"
        )
        context.bot.send_message(chat_id="-1002275382452",
                                 text=adm_msg,
                                 parse_mode='HTML',
                                 )
    except Exception as e:
        print(e)
    update.message.reply_text(
        f"Balanse ko'paytirildi!\nFoydalanuvchini hozirgi balanse: {user_account.current_price} so'm",
    )
    return state.ADMIN


def send_msg(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if not admins.exists():
        update.message.reply_text("Sizda bu amallarni bajarish huquqi yo'q!")
        return ConversationHandler.END
    user_chat_id = context.chat_data['chat_id']
    try:
        update.message.copy(
            user_chat_id
        )
        update.message.reply_text(
            "Xabaringiz muvafaqiyatli yuborildi ✅"
        )
    except Exception as e:
        update.message.reply_text(
            f"Xabaringiz yuborilmadi ❌ \nERROR: {e}"
        )
    return state.ADMIN


def get_all_stories(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        promo_codes = StoryBonusAccounts.objects.filter(is_active=True).order_by('-created_at')[:50]
        if promo_codes.exists():
            msg = f"✅ <b>Oxirgi 50 ta aktiv storieslar</b>\n\n"
            counter = 1
            for promo_code in promo_codes:
                custom_user = CustomUser.objects.get(chat_id=promo_code.chat_id)
                fullname = custom_user.first_name if custom_user.first_name else '-' + " " + custom_user.last_name if custom_user.last_name else '-'
                minio = f"<a href='tg://user?id={custom_user.chat_id}'>{fullname}</a>"
                msg += f"{counter}). {minio}, {promo_code.created_at.date()}, +{custom_user.phone_number}, @{custom_user.username}\n"
                counter += 1

            update.message.reply_html(msg)
        else:
            update.message.reply_html(
                "Hozirda aktiv storieslar mavjud emas!"
            )


def add_promo_code(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        update.message.reply_html(
            "<b>Promo kod qo'shish uchun quyidagi formatda yuboring:</b>\n\n"
            "<code>promo_kod+soni+qiymati</code>"
            "\n\nMasalan: <code>promo123+1000+5</code> - bu promo kodni 1000 ta 5💎 qo'shadi.",

            reply_markup=keyword.back()
        )
        return state.ADD_PROMO_CODE


def get_promo_code(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        promo_code = update.message.text.strip()
        parts = promo_code.split('+')
        if len(parts) == 3:
            code, count, price = parts
            try:
                count = int(count)
                price = float(price)
                if count > 0 and price > 0:
                    CustomPromoCode.objects.get_or_create(
                        name=code,
                        status=True,
                        defaults={
                            'count': count,
                            'reward': price,
                            'default': count,
                        })
                    update.message.reply_html(f"✅ Promo kod <code>{code}</code> muvaffaqiyatli qo'shildi!")
                else:
                    update.message.reply_html("❌ Iltimos, soni va qiymatini musbat raqamlar sifatida kiriting.")
            except ValueError:
                update.message.reply_html("❌ Iltimos, soni va qiymatini to'g'ri formatda kiriting.")
        else:
            update.message.reply_html(
                "❌ Iltimos, promo kodni to'g'ri formatda kiriting: <code>promo_kod+soni+qiymati</code>")


def check_custom_promo_code(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        update.message.reply_html(
            "<b>Promo kodni kiriting:</b>\n\n"
            "<code>promo_kod</code>\n\nMasalan: <code>promo123</code>",
            reply_markup=keyword.back()
        )
        return state.CHECK_CUSTOM_PROMO_CODE


def get_custom_promo_code(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        promo_code = update.message.text.strip()
        promo = CustomPromoCode.objects.filter(name=promo_code, status=True).first()
        if promo:
            update.message.reply_html(
                f"✅ <b>Promo kod topildi!</b>\n\n"
                f"🆔 Promo KOD: <code>{promo.name}</code>\n"
                f"📊 Promo soni: <code>{promo.default}</code>\n"
                f"📊 Promo qoldi: <code>{promo.count}</code>\n"
                f"💰 Promo qiymat: <code>{promo.reward}</code> 💎\n"
                f"📅 Promo vaqti: <code>{promo.created_at.date()}</code>"
            )
        else:
            update.message.reply_html("❌ Bu promo kod topilmadi yoki passiv holatda!")


def stats(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        all_user_count = CustomUser.objects.all().count()
        all_block_count = CustomUser.objects.filter(is_blocked=True).count()
        active_count = CustomUser.objects.filter(is_active=True).count()
        msg = f"""
📊 <b>Umumiy Statistika</b>

👤 <i>Foydalanuvchilar soni:</i> <code>{all_user_count}</code>
🔐 <i>Bloklanganlar soni:</i> <code>{all_block_count}</code>
✅ <i>Aktivlar soni:</i> <code>{active_count}</code>
"""
        update.message.reply_html(msg, reply_markup=keyword.admin_base())


def unban(update: Update, context: CallbackContext):
    if update.message.chat_id in [749750897, 758934089]:
        all_block_count = CustomUser.objects.filter(is_blocked=True).count()

        # O'zbek raqamlar
        uzb_blocked_users = CustomUser.objects.filter(
            is_blocked=True,
            phone_number__regex=r'^\+?998'
        )

        # Qolgan raqamlar
        other_blocked_users = CustomUser.objects.filter(
            is_blocked=True
        ).exclude(
            phone_number__regex=r'^\+?998'
        )

        msg = f"""
📊 <b>Umumiy Blocklanganlar</b>

🔐 <i>Bloklanganlar soni:</i> <code>{all_block_count}</code>
🇺🇿 <i>O'zbek nomerlar bloklangan:</i> <code>{uzb_blocked_users.count()}</code>
🌐 <i>Boshqa nomerlar bloklangan:</i> <code>{other_blocked_users.count()}</code>
"""
        update.message.reply_html(msg, reply_markup=keyword.confirm_unban())
        return state.CANCEL_UNBAN


def cancel_unban(update: Update, context: CallbackContext):
    admins = CustomUser.objects.filter(is_admin=True, chat_id=update.effective_chat.id)
    if admins.exists():
        count = uzb_blocked_users = CustomUser.objects.filter(
            is_blocked=True,
            phone_number__regex=r'^\+?998'
        ).count()
        CustomUser.objects.filter(
            is_blocked=True,
            phone_number__regex=r'^\+?998'
        ).update(is_blocked=False, is_active=True)

        update.message.reply_html(
            f"✅ <b>O'zbek raqamlar blokdan chiqarildi:</b> <code>{count}</code>",
            reply_markup=keyword.admin_base()
        )
        return state.ADMIN
