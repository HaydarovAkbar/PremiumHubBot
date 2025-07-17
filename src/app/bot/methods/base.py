import time
from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, CustomUserAccount
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
        context.bot.send_photo(chat_id=update.effective_user.id,
                               photo='AgACAgIAAxkBAAEaMCdoeJzgVCgsP05l79z72EpYtLSnfAACB_oxG14bwUsodGhV1zrgcAEAAwIAA3kAAzYE',
                               caption="Botni ishga tushirish uchun quyidagi kanallarga obuna bo’ling va “♻️ Tekshirish” tugmasini bosing",
                               reply_markup=keyword.channels(left_channel))
        # context.bot.send_message(chat_id=update.effective_user.id,
        #                          text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling)",
        #                          reply_markup=keyword.channels(left_channel))
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
        # context.bot.send_message(chat_id=update.effective_user.id,
        #                          text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling",
        #                          reply_markup=keyword.channels(left_channel))
        context.bot.send_photo(chat_id=update.effective_user.id,
                               photo='AgACAgIAAxkBAAEaMCdoeJzgVCgsP05l79z72EpYtLSnfAACB_oxG14bwUsodGhV1zrgcAEAAwIAA3kAAzYE',
                               caption="Botni ishga tushirish uchun quyidagi kanallarga obuna bo’ling va “♻️ Tekshirish” tugmasini bosing",
                               reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    return start(update, context)


def start(update: Update, context: CallbackContext):
    payload = context.args[0] if context.args else None
    user, _ = CustomUser.objects.get_or_create(chat_id=update.effective_user.id, defaults={
        'username': update.effective_user.username,
        'first_name': update.effective_user.first_name,
        'last_name': update.effective_user.last_name,
        'is_active': False,
        'referral': payload,
    })
    user.first_name = update.effective_user.first_name
    user.last_name = update.effective_user.last_name
    user.username = update.effective_user.username
    user.save()
    if _:
        if payload:
            context.chat_data['payload'] = payload
            try:
                payload = int(payload)
                user = update.effective_user
                mention = f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"
                context.bot.send_message(chat_id=payload,
                                         text=f"""
👏 Tabriklaymiz! Siz {mention} ni botga taklif qildingiz!

<i>Do'stingiz ro'yxatdan o'tganidan keyin, biz sizga referal puli taqdim etamiz!</i>""",
                                         parse_mode=ParseMode.HTML
                                         )
            except CustomUser.DoesNotExist:
                payload = None
    all_channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for channel in all_channel:
        try:
            a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(channel)
        except Exception:
            pass
    if left_channel:
        # context.bot.send_message(chat_id=update.effective_user.id,
        #                          text="Botni ishga tushirish uchun quyidagi kanallarga obuna bo’ling va “♻️ Tekshirish” tugmasini bosing",
        #                          reply_markup=keyword.channels(left_channel))
        context.bot.send_photo(chat_id=update.effective_user.id,
                               photo='AgACAgIAAxkBAAEaMCdoeJzgVCgsP05l79z72EpYtLSnfAACB_oxG14bwUsodGhV1zrgcAEAAwIAA3kAAzYE',
                               caption="Botni ishga tushirish uchun quyidagi kanallarga obuna bo’ling va “♻️ Tekshirish” tugmasini bosing",
                               reply_markup=keyword.channels(left_channel))

        return state.CHECK_CHANNEL
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
                                     text="""🔁 Botimiz yangilangani va xavfsizlikni oshirish munosabati bilan quyidagi havola orqali ro’yxatdan o’ting va botni ishlatishda davom eting
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
    user_contact = update.message.contact.phone_number
    if user_contact.startswith('+998') or user_contact.startswith('998'):
        user.phone_number = update.message.contact.phone_number
        user.save()
        if not user.is_active:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="""🔁Botimiz yangilangani va xavfsizlikni oshirish munosabati bilan quyidagi havola orqali ro’yxatdan o’ting va botni ishlatishda davom eting""",
                                     parse_mode='HTML',
                                     reply_markup=keyword.signup(settings.SIGNUP_URL))
            return state.SIGNUP
        update.message.reply_html(msg.BASE_MSG, reply_markup=keyword.base())
        return state.START
    else:
        update.message.reply_html(
            "<b>Botdan foydalanish uchun faqat UZB telefon nomer orqali ochilgan akkountingiz bo'lishi kerak</b>")
        user.delete()


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


def manual(update: Update, context: CallbackContext):
    file_id = msg.manual_video_id
    _msg_ = """
1. Doʻstlaringizni taklif qiling  <b>«Telegram Premium yoki Telegram Stars» </b>oling .

2. Bonuslar orqali turlixil topshiriqlarni bajarib ossongina olmoslar yig'ing 

3. Referal yigʻish maqsadida turli xil yolgʻon soʻzlar bilan reklama tarqatmang! Zero, qalb xotirjamligining asosi rostgoʻylikdir.

Bular haqida toʻliq maʼlumot olish uchun maxsus qoʻllanmalar bilan tanishib chiqing 👇

<b>• Botda roʻyxatdan oʻtish uchun qoʻllanma: </b>
t.me/premium_olish_qollanmasi/21

<b>• Botda foydalanish hamda olmoslar yigib  Premium va Stars olish usuli: </b>
t.me/premium_olish_qollanmasi/22

<b>• Topshiriqlar hamda Kunlik Bonuslar: </b>
t.me/premium_olish_qollanmasi/23

    """
    update.message.reply_video(
        video=file_id,
        caption=_msg_,
        parse_mode='HTML',
    )


def adminstrator(update: Update, context: CallbackContext):
    _msg_ = """<b> 📞 Premium uchun: @Premium_xizmatim

🛠 Savollar uchun: @Hup_support

💬 Chat: @Premiumhub_chat</b>
    """
    update.message.reply_html(_msg_)
