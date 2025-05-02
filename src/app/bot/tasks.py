# app/bot/tasks.py
import telegram
from celery import shared_task
import time
from telegram.error import RetryAfter
from app.models import CustomUser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from celery.result import AsyncResult


@shared_task(bind=True, ignore_result=True)
def send_advert_to_all(self, chat_id, message_id, button_data=None, ads_text=None):
    if self.request.called_directly is False:
        if AsyncResult(self.request.id).state == 'REVOKED':
            print("Task to‘xtatilgan")
            return

    from .main import bot
    BATCH_SIZE = 5000
    count = 0
    last_id = 0
    if button_data:

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(b["text"], url=b["url"])] for b in button_data
        ])
        while True:
            users = list(CustomUser.objects.filter(id__gt=last_id).order_by('id')[:BATCH_SIZE])
            if not users:
                break

            for user in users:
                try:
                    # bot.copy_message(
                    #     chat_id=user.chat_id,
                    #     from_chat_id=chat_id,
                    #     message_id=message_id,
                    #     reply_markup=markup
                    # )
                    bot.send_message(
                        chat_id=user.chat_id,
                        text=ads_text,
                        reply_markup=markup,
                        parse_mode=telegram.ParseMode.HTML
                    )
                    count += 1
                except RetryAfter as e:
                    time.sleep(e.retry_after)
                    continue
                except Exception as e:
                    # print(f"❌ Xatolik foydalanuvchiga yuborishda: {e}")
                    continue

                if count % 20 == 0:
                    time.sleep(1.5)

            last_id = users[-1].id
            admins = CustomUser.objects.filter(is_admin=True).order_by('id')
            if count % (BATCH_SIZE * 5) == 0:
                for admin in admins:
                    try:
                        bot.send_message(
                            chat_id=admin.chat_id,
                            text=f"""
        📊 <b>Xabaringiz {last_id} dan {count} ga yuborildi! ☑️</b>

        🕞 Yuborish davom etmoqda!
            """,
                            parse_mode=telegram.ParseMode.HTML,
                        )
                    except Exception:
                        pass
    else:
        markup = None

        while True:
            users = list(CustomUser.objects.filter(id__gt=last_id).order_by('id')[:BATCH_SIZE])
            if not users:
                break

            for user in users:
                try:
                    bot.copy_message(
                        chat_id=user.chat_id,
                        from_chat_id=chat_id,
                        message_id=message_id,
                        reply_markup=markup
                    )
                    count += 1
                except RetryAfter as e:
                    time.sleep(e.retry_after)
                    continue
                except Exception as e:
                    # print(f"❌ Xatolik foydalanuvchiga yuborishda: {e}")
                    continue

                if count % 20 == 0:
                    time.sleep(1.5)

            last_id = users[-1].id
            admins = CustomUser.objects.filter(is_admin=True).order_by('id')
            if count % (BATCH_SIZE * 5) == 0:
                for admin in admins:
                    try:
                        bot.send_message(
                            chat_id=admin.chat_id,
                            text=f"""
        📊 <b>Xabaringiz {last_id} dan {count} ga yuborildi! ☑️</b>
            
        🕞 Yuborish davom etmoqda!
            """,
                            parse_mode=telegram.ParseMode.HTML,
                        )
                    except Exception:
                        pass
    admins = CustomUser.objects.filter(is_admin=True).order_by('id')
    for admin in admins:
        try:
            bot.send_message(
                chat_id=admin.chat_id,
                text=f"""
📊 <b>Xabaringiz yakunlandi {last_id} dan {count} ga yuborildi! ✅</b>
    """,
                parse_mode=telegram.ParseMode.HTML,
            )
        except Exception:
            pass
    return f"Reklama yuborildi. Jami foydalanuvchilar: {count}"
