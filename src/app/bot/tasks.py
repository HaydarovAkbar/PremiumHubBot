# app/bot/tasks.py
from celery import shared_task
import time
from app.models import CustomUser, TopUser
from celery.result import AsyncResult
from django.conf import settings
import requests
from html import escape

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


TELEGRAM_BOT_TOKEN = settings.TOKEN
GROUP_CHAT_ID = -1002275382452  # O'zgartiring

MAX_TG_LEN = 4096
SAFE_MARGIN = 200  # sarlavha/formatlash uchun buffer

def _chunk_and_send(text: str) -> None:
    """
    Telegram 4096 limitini hisobga olib, matnni bo'lib-bo'lib yuboradi.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    start = 0
    while start < len(text):
        end = min(len(text), start + MAX_TG_LEN - SAFE_MARGIN)
        # bo'lakni qator bo'yicha bo'lib yuboramiz
        if end < len(text):
            nl = text.rfind("\n", start, end)
            if nl > start:
                end = nl
        chunk = text[start:end]
        r = requests.post(url, data={
            "chat_id": GROUP_CHAT_ID,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=20)
        r.raise_for_status()
        start = end

@shared_task
def reset_weekly_earned_and_send_report() -> str:
    """
    Haftalik Top 10 hisobotini guruhga yuboradi va so'ng weekly_earned ni 0 ga tushiradi.
    HTML-escape qo'llangan; xabar uzun bo'lsa bo'lib yuboriladi.
    """
    # 1) Top10 ni o'qiymiz
    top_users = list(TopUser.objects.order_by('-weekly_earned')[:10])

    # Top bo'sh bo'lsa – faqat xabar yuboramiz
    if not top_users:
        info = "📊 <b>Haftalik Top:</b>\n\nHali natijalar yo‘q."
        try:
            _chunk_and_send(info)
        except Exception as e:
            return f"Xabar yuborishda xatolik (bo'sh): {e}"
        # Reset shart emas, lekin baribir:
        TopUser.objects.update(weekly_earned=0)
        return "Bo'sh top yuborildi va weekly_earned tozalandi"

    # 2) Hisobot matni (HTML-escape!)
    lines = ["📊 <b>Haftalik Top 10 foydalanuvchilar:</b>", ""]
    for idx, u in enumerate(top_users, 1):
        name = escape(u.fullname or str(u.chat_id))
        # 💎 ishlatayotganingiz uchun “so'm” emas, emoji qoldirdim; xohlasangiz ' so\'m' deb yozing
        lines.append(f"{idx}. {name} — {u.weekly_earned:,} 💎")
    report = "\n".join(lines)

    # 3) Yuborish (bo'lib yuboradi)
    try:
        _chunk_and_send(report)
    except Exception as e:
        return f"Xabar yuborishda xatolik: {e}"

    # 4) Reset
    TopUser.objects.update(weekly_earned=0)
    return "Top yuborildi va weekly_earned tozalandi"
