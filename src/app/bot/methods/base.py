import time
from django.conf import settings
from telegram import Update
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
    payload = context.args[0] if context.args else None
    if payload:
        try:
            payload = int(payload)
            # payload_user = CustomUser.objects.get(chat_id=payload)
            context.bot.send_message(chat_id=payload,
                                     text=f"""
👏 Tabriklaymiz! Siz {update.effective_chat.full_name}ni botga taklif qildingiz!
  
Do'stingiz ro'yxatdan o'tganidan keyin, biz sizga referal puli taqdim etamiz!""")
        except CustomUser.DoesNotExist:
            pass

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
        'referral': payload,
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


def manual(update: Update, context: CallbackContext):
    file_id = msg.manual_video_id
    _msg_ = """
1. Doʻstlaringizni taklif qiling va pul yigʻing. Yigʻilgan pulni <b>«Telegram Premium yoki Telegram Stars»</b>ga almashtiring.

2. Premiumingiz boʻlsa, kanalimizga ovoz berish orqali har kunlik bonuslarni olishingiz va <b>«Telegram Premium yoki Telegram Stars»</b>ga ishlatishingiz mumkin

3. Referal yigʻish maqsadida turli xil yolgʻon soʻzlar bilan reklama tarqatmang! Zero, qalb xotirjamligining asosi rostgoʻylikdir.

Bular haqida toʻliq maʼlumot olish uchun maxsus qoʻllanmalar bilan tanishib chiqing 👇

<b>• Botda roʻyxatdan oʻtish uchun qoʻllanma: </b>
t.me/premium_olish_qollanmasi/3

<b>• Premium olish uchun botda pul ishlash ketma-ketligi: </b>
t.me/premium_olish_qollanmasi/4

<b>• Botda pul yigʻib Premium olish usuli: </b>
t.me/premium_olish_qollanmasi/5

<b>• Menga uzoq muddatli Premium obunasi kerak desangiz: </b>
t.me/premium_olish_qollanmasi/6
    """
    update.message.reply_video(
        video=file_id,
        caption=_msg_,
        parse_mode='HTML',
    )


# def adminstrator(update: Update, context: CallbackContext):
#     _msg_ = """<b>
# 📞 Premium uchun: @Premium_xizmatim
#
# 🛠 Savollar uchun: @Hup_support
#
# 💬 Chat: @Premiumhub_chat</b>
#     """
#     update.message.reply_html(
#         _msg_,
#     )
#
#     import pymysql
#
#     # MySQL ulanish parametrlari
#     host = "109.73.201.204"
#     user = "premium_bot"
#     password = "Shohzod1009"
#     database = "premium_bot"
#
#     batch_size = 1000
#     offset = 0
#
#     try:
#         # Ulanishni amalga oshirish
#         connection = pymysql.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database
#         )
#         print("✅ Muvaffaqiyatli ulandi!")
#
#         with connection.cursor() as cursor:
#             query = f"SELECT * FROM users LIMIT {batch_size} OFFSET {offset}"
#             cursor.execute(query)
#             rows = cursor.fetchall()
#
#             # # Natijalarni chiqarish
#             # for row in rows:
#             #     print(row)
#             counter = 1
#             for row in rows:
#                 if counter % 500 == 0:
#                     print(f"{counter}. {row} kiritildi.")
#                 if row[3] == 'false':
#                     is_blocked = False
#                 if row[3] == 'true':
#                     is_blocked = True
#                 else:
#                     is_blocked = False
#
#                 custom_user, _ = CustomUser.objects.get_or_create(
#                     chat_id=row[1],
#                     # phone_number=row[10],
#                     # is_blocked=is_blocked,
#                     # is_active=False,
#                     # referral=row[5],
#                     defaults={
#                         'is_blocked': is_blocked,
#                         'phone_number': row[10],
#                         'is_active': False,
#                         'referral': row[5],
#                     }
#                 )
#                 custom_user_account, __ = CustomUserAccount.objects.get_or_create(
#                     chat_id=row[1],
#                     defaults={
#                         'current_price': row[4] if row[4] != None else 0,
#                         'total_price': row[4] if row[4] != None else 0,
#                     }
#                 )
#                 counter += 1
#                 time.sleep(0.1)
#
#     except Exception as e:
#         print("❌ Xatolik yuz berdi:", e)
#
#     finally:
#         if 'connection' in locals():
#             connection.close()

def adminstrator(update: Update, context: CallbackContext):
    _msg_ = """<b>
📞 Premium uchun: @Premium_xizmatim

🛠 Savollar uchun: @Hup_support

💬 Chat: @Premiumhub_chat</b>
    """
    update.message.reply_html(_msg_)

    import pymysql
    import time

    host = "109.73.201.204"
    user = "premium_bot"
    password = "Shohzod1009"
    database = "premium_bot"

    batch_size = 1000
    offset = 0

    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("✅ Muvaffaqiyatli ulandi!")
        exceptions_list = []
        while True:
            with connection.cursor() as cursor:
                query = f"SELECT * FROM users LIMIT {batch_size} OFFSET {offset}"
                cursor.execute(query)
                rows = cursor.fetchall()

                if not rows:
                    print("✅ Barcha ma'lumotlar o'qib bo'lindi.")
                    break

                print(f"📦 {len(rows)} ta yozuv olib kelindi (offset={offset})")

                for row in rows:
                    try:
                        is_blocked = True if row[3] == 'true' else False

                        custom_user, _ = CustomUser.objects.get_or_create(
                            chat_id=row[1],
                            defaults={
                                'is_blocked': is_blocked,
                                'phone_number': row[10],
                                'is_active': False,
                                'referral': row[5],
                            }
                        )
                        custom_user_account, __ = CustomUserAccount.objects.get_or_create(
                            chat_id=row[1],
                            defaults={
                                'current_price': row[4] if row[4] is not None else 0,
                                'total_price': row[4] if row[4] is not None else 0,
                            }
                        )

                        time.sleep(0.1)  # yoki 0.1 sekunddan kamroq yuklama bo'lsa
                    except Exception as e:
                        exceptions_list.append(row[1])

                offset += batch_size
            print(exceptions_list)
    except Exception as e:
        print("❌ Xatolik yuz berdi:", e)

    finally:
        if 'connection' in locals():
            connection.close()
