# app/bot/tasks.py
import telegram
from celery import shared_task
import time
from telegram.error import RetryAfter
from app.models import CustomUser, TopUser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from celery.result import AsyncResult
from django.conf import settings
import requests

# @shared_task(bind=True, ignore_result=True)
# def send_advert_to_all(self, chat_id, message_id, button_data=None, ads_text=None):
#     if self.request.called_directly is False:
#         if AsyncResult(self.request.id).state == 'REVOKED':
#             print("Task to‘xtatilgan")
#             return
#
#     from .main import bot
#     BATCH_SIZE = 5000
#     count = 0
#     last_id = 0
#     if button_data:
#
#         markup = InlineKeyboardMarkup([
#             [InlineKeyboardButton(b["text"], url=b["url"])] for b in button_data
#         ])
#         while True:
#             users = list(CustomUser.objects.filter(id__gt=last_id).order_by('id')[:BATCH_SIZE])
#             if not users:
#                 break
#
#             for user in users:
#                 try:
#                     # bot.copy_message(
#                     #     chat_id=user.chat_id,
#                     #     from_chat_id=chat_id,
#                     #     message_id=message_id,
#                     #     reply_markup=markup
#                     # )
#                     bot.send_message(
#                         chat_id=user.chat_id,
#                         text=ads_text,
#                         reply_markup=markup,
#                         parse_mode=telegram.ParseMode.HTML
#                     )
#                     count += 1
#                 except RetryAfter as e:
#                     time.sleep(e.retry_after)
#                     continue
#                 except Exception as e:
#                     # print(f"❌ Xatolik foydalanuvchiga yuborishda: {e}")
#                     continue
#
#                 if count % 20 == 0:
#                     time.sleep(1.5)
#
#             last_id = users[-1].id
#             admins = CustomUser.objects.filter(is_admin=True).order_by('id')
#             if count % (BATCH_SIZE * 5) == 0:
#                 for admin in admins:
#                     try:
#                         bot.send_message(
#                             chat_id=admin.chat_id,
#                             text=f"""
#         📊 <b>Xabaringiz {last_id} dan {count} ga yuborildi! ☑️</b>
#
#         🕞 Yuborish davom etmoqda!
#             """,
#                             parse_mode=telegram.ParseMode.HTML,
#                         )
#                     except Exception:
#                         pass
#     else:
#         while True:
#             users = list(CustomUser.objects.filter(id__gt=last_id).order_by('id')[:BATCH_SIZE])
#             if not users:
#                 break
#
#             for user in users:
#                 try:
#                     bot.copy_message(
#                         chat_id=user.chat_id,
#                         from_chat_id=chat_id,
#                         message_id=message_id,
#                     )
#                     count += 1
#                 except RetryAfter as e:
#                     time.sleep(e.retry_after)
#                     continue
#                 except Exception as e:
#                     # print(f"❌ Xatolik foydalanuvchiga yuborishda: {e}")
#                     continue
#
#                 if count % 20 == 0:
#                     time.sleep(1.5)
#
#             last_id = users[-1].id
#             admins = CustomUser.objects.filter(is_admin=True).order_by('id')
#             if count % (BATCH_SIZE * 5) == 0:
#                 for admin in admins:
#                     try:
#                         bot.send_message(
#                             chat_id=admin.chat_id,
#                             text=f"""
#         📊 <b>Xabaringiz {last_id} dan {count} ga yuborildi! ☑️</b>
#
#         🕞 Yuborish davom etmoqda!
#             """,
#                             parse_mode=telegram.ParseMode.HTML,
#                         )
#                     except Exception:
#                         pass
#     admins = CustomUser.objects.filter(is_admin=True).order_by('id')
#     for admin in admins:
#         try:
#             bot.send_message(
#                 chat_id=admin.chat_id,
#                 text=f"""
# 📊 <b>Xabaringiz yakunlandi {last_id} dan {count} ga yuborildi! ✅</b>
#     """,
#                 parse_mode=telegram.ParseMode.HTML,
#             )
#         except Exception:
#             pass
#     return f"Reklama yuborildi. Jami foydalanuvchilar: {count}"


# ---------------------------------------------->
API_TOKEN = settings.TOKEN
API_URL = f"https://api.telegram.org/bot{API_TOKEN}/"


@shared_task(bind=True, ignore_result=True)
def send_advert_to_all(self, chat_id, message_id, method="copyMessage", button_data=None, ads_text=None):
    if not self.request.called_directly and AsyncResult(self.request.id).state == 'REVOKED':
        print("Task to‘xtatilgan")
        return

    BATCH_SIZE = 5000
    count = 0
    last_id = 0

    while True:
        users = list(CustomUser.objects.filter(id__gt=last_id).order_by('id')[:BATCH_SIZE])
        if not users:
            break

        for user in users:
            try:
                payload = {}

                # if method == 'sendMessage':
                #     payload = {
                #         "chat_id": user.chat_id,
                #         "text": ads_text,
                #         "parse_mode": "HTML"
                #     }
                #     if button_data:
                #         payload["reply_markup"] = {
                #             "inline_keyboard": [[{"text": b["text"], "url": b["url"]}] for b in button_data]
                #         }

                if method == 'copyMessage':
                    payload = {
                        "chat_id": user.chat_id,
                        "from_chat_id": chat_id,
                        "message_id": message_id
                    }
                    if button_data:
                        payload["reply_markup"] = {
                            "inline_keyboard": [[{"text": b["text"], "url": b["url"]}] for b in button_data]
                        }

                elif method == 'forwardMessage':
                    payload = {
                        "chat_id": user.chat_id,
                        "from_chat_id": chat_id,
                        "message_id": message_id
                    }
                else:
                    payload = {
                        "chat_id": user.chat_id,
                        "from_chat_id": chat_id,
                        "message_id": message_id
                    }
                    if button_data:
                        payload["reply_markup"] = {
                            "inline_keyboard": [[{"text": b["text"], "url": b["url"]}] for b in button_data]
                        }

                requests.post(f"{API_URL}{method}", json=payload)
                count += 1

            except requests.exceptions.RequestException:
                continue

            if count % 20 == 0:
                time.sleep(1.5)

        last_id = users[-1].id
        if count % (BATCH_SIZE * 5) == 0:
            for admin in CustomUser.objects.filter(is_admin=True):
                try:
                    requests.post(API_URL + "sendMessage", json={
                        "chat_id": admin.chat_id,
                        "text": f"📊 <b>Xabaringiz {last_id} dan {count} ga yuborildi! ☑️</b>\n\n🕞 Yuborish davom etmoqda!",
                        "parse_mode": "HTML"
                    })
                except:
                    pass

    for admin in CustomUser.objects.filter(is_admin=True):
        try:
            requests.post(API_URL + "sendMessage", json={
                "chat_id": admin.chat_id,
                "text": f"📊 <b>Xabaringiz yakunlandi {last_id} dan {count} ga yuborildi! ✅</b>",
                "parse_mode": "HTML"
            })
        except:
            pass

    return f"Reklama yuborildi. Jami foydalanuvchilar: {count}"


# @shared_task(bind=True, ignore_result=True)
# def send_advert_to_all(self, ads_update, button_data=None):
#     if self.request.called_directly is False:
#         if AsyncResult(self.request.id).state == 'REVOKED':
#             print("Task to‘xtatilgan")
#             return
#
#     from .main import bot
#     BATCH_SIZE = 5000
#     count = 0
#     last_id = 0
#     if button_data:
#
#         markup = InlineKeyboardMarkup([
#             [InlineKeyboardButton(b["text"], url=b["url"])] for b in button_data
#         ])
#         while True:
#             users = list(CustomUser.objects.filter(id__gt=last_id).order_by('id')[:BATCH_SIZE])
#             if not users:
#                 break
#
#             for user in users:
#                 try:
#                     # bot.copy_message(
#                     #     chat_id=user.chat_id,
#                     #     from_chat_id=chat_id,
#                     #     message_id=message_id,
#                     #     reply_markup=markup
#                     # )
#                     # bot.send_message(
#                     #     chat_id=user.chat_id,
#                     #     text=ads_text,
#                     #     reply_markup=markup,
#                     #     parse_mode=telegram.ParseMode.HTML
#                     # )
#                     ads_update.copy(
#                         chat_id=user.chat_id,
#                         reply_markup=markup,
#                     )
#                     count += 1
#                 except RetryAfter as e:
#                     time.sleep(e.retry_after)
#                     continue
#                 except Exception as e:
#                     # print(f"❌ Xatolik foydalanuvchiga yuborishda: {e}")
#                     continue
#
#                 if count % 20 == 0:
#                     time.sleep(1.5)
#
#             last_id = users[-1].id
#             admins = CustomUser.objects.filter(is_admin=True).order_by('id')
#             if count % (BATCH_SIZE * 5) == 0:
#                 for admin in admins:
#                     try:
#                         bot.send_message(
#                             chat_id=admin.chat_id,
#                             text=f"""
#         📊 <b>Xabaringiz {last_id} dan {count} ga yuborildi! ☑️</b>
#
#         🕞 Yuborish davom etmoqda!
#             """,
#                             parse_mode=telegram.ParseMode.HTML,
#                         )
#                     except Exception:
#                         pass
#     else:
#
#         while True:
#             users = list(CustomUser.objects.filter(id__gt=last_id).order_by('id')[:BATCH_SIZE])
#             if not users:
#                 break
#
#             for user in users:
#                 try:
#                     ads_update.copy(
#                         chat_id=user.chat_id,
#                     )
#                     count += 1
#                 except RetryAfter as e:
#                     time.sleep(e.retry_after)
#                     continue
#                 except Exception as e:
#                     # print(f"❌ Xatolik foydalanuvchiga yuborishda: {e}")
#                     continue
#
#                 if count % 20 == 0:
#                     time.sleep(1.5)
#
#             last_id = users[-1].id
#             admins = CustomUser.objects.filter(is_admin=True).order_by('id')
#             if count % (BATCH_SIZE * 5) == 0:
#                 for admin in admins:
#                     try:
#                         bot.send_message(
#                             chat_id=admin.chat_id,
#                             text=f"""
#         📊 <b>Xabaringiz {last_id} dan {count} ga yuborildi! ☑️</b>
#
#         🕞 Yuborish davom etmoqda!
#             """,
#                             parse_mode=telegram.ParseMode.HTML,
#                         )
#                     except Exception:
#                         pass
#     admins = CustomUser.objects.filter(is_admin=True).order_by('id')
#     for admin in admins:
#         try:
#             bot.send_message(
#                 chat_id=admin.chat_id,
#                 text=f"""
# 📊 <b>Xabaringiz yakunlandi {last_id} dan {count} ga yuborildi! ✅</b>
#     """,
#                 parse_mode=telegram.ParseMode.HTML,
#             )
#         except Exception:
#             pass
#     return f"Reklama yuborildi. Jami foydalanuvchilar: {count}"


TELEGRAM_BOT_TOKEN = settings.TOKEN
GROUP_CHAT_ID = -1002275382452  # O'zgartiring


@shared_task
def reset_weekly_earned_and_send_report():
    top_users = TopUser.objects.order_by('-weekly_earned')[:10]

    if not top_users:
        return "Top userlar yo‘q"

    report_lines = ["📊 *Haftalik Top 10 foydalanuvchilar:*"]
    for idx, user in enumerate(top_users, 1):
        report_lines.append(f"{idx}. {user.fullname} — {user.weekly_earned:,} so'm")

    report = "\n".join(report_lines)

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': GROUP_CHAT_ID,
        'text': report,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)

    if response.status_code != 200:
        return f"Xabar yuborishda xatolik: {response.text}"

    TopUser.objects.update(weekly_earned=0)

    return "Top userlar yuborildi va weekly_earned tozalandi"
