# app/bot/tasks.py

from celery import shared_task
import time
from telegram.error import RetryAfter
from app.models import CustomUser


@shared_task
def send_advert_to_all(chat_id, message_id):
    print("salom")
    from .main import bot
    BATCH_SIZE = 5000
    count = 0
    last_id = 0

    while True:
        users = CustomUser.objects.filter(id__gt=last_id).order_by('id')[:BATCH_SIZE]
        if not users:
            break

        for user in users:
            try:
                bot.copy_message(
                    chat_id=user.telegram_id,
                    from_chat_id=chat_id,
                    message_id=message_id
                )
                count += 1
            except RetryAfter as e:
                time.sleep(e.retry_after)
                continue
            except Exception:
                continue

            if count % 20 == 0:
                time.sleep(1.5)

        last_id = users.last().id
    return "Reklama yuborildi"
