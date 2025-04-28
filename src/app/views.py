from django.shortcuts import render
from django.http import HttpResponse
from telegram import Update
from .bot.main import bot, dispatcher
from django.utils.decorators import method_decorator
from django.views import View
import json
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import CustomUser, Settings, CustomUserAccount, TopUser
from telegram import Bot
from .bot.keyboards.base import Keyboards
from django.conf import settings
import requests


def is_premium_user(user_id: int, bot_token: str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    response = requests.post(url, data={"chat_id": user_id})

    if response.status_code == 200:
        data = response.json()
        return data.get("result", {}).get("is_premium", False)
    return False


@method_decorator(csrf_exempt, name='dispatch')
class MainView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('GET request')

    def post(self, request, *args, **kwargs):
        try:
            body = request.body
            body_json = json.loads(body)
            update: Update = Update.de_json(body_json, bot)
            dispatcher.process_update(update)
        except Exception as e:
            print(e)
        return HttpResponse('POST request')


def signup_view(request):
    return render(request, 'signup.html')


def stories_bonus(request):
    context = {
        'video_url': f'{settings.HOST}/static/videos/stories.mp4'
    }
    return render(request, 'story.html', context)


@csrf_exempt
def register_device(request):
    if request.method == "POST":
        data = json.loads(request.body)

        model = data.get("model")
        d_type = data.get("tur")
        lang = data.get("til")
        memory = str(data.get("hotira"))
        telegram_id = int(data.get("telegram_id"))
        raw_string = model + d_type + lang + memory
        fingerprint_hash = hashlib.sha256(raw_string.encode()).hexdigest()
        existing = CustomUser.objects.filter(
            device_hash=fingerprint_hash
        ).count()
        bot_settings = Settings.objects.filter(is_active=True).last()
        custom_user = CustomUser.objects.get(chat_id=telegram_id)
        if existing >= bot_settings.device_count:
            custom_user.is_blocked = True
            custom_user.is_active = False
            custom_user.save()
            bot.send_message(
                chat_id=telegram_id,
                text=(
                    "❌ Bu qurilmadan allaqachon boshqa foydalanuvchi foydalanmoqda.\n\n"
                    f"✅ Botdan faqat {bot_settings.device_count} ta qurilmada foydalanish mumkin.\n\n"
                    "Agar buni xato deb hisoblasangiz, @hup_support ga murojaat qiling"
                )
            )
            return JsonResponse({
                "error": "Bu qurilma boshqa foydalanuvchi tomonidan ishlatilgan."
            }, status=403)

        if not (custom_user.device_hash and custom_user.is_active):
            custom_user.device_hash = fingerprint_hash
            custom_is_premium = is_premium_user(custom_user.chat_id, settings.TOKEN)
            custom_user_ref_price = bot_settings.referral_prem_price if custom_is_premium else bot_settings.referral_price
            custom_user.is_active = True
            custom_user.save()
            keyword = Keyboards()
            try:
                referral_user = CustomUser.objects.get(chat_id=custom_user.referral)
                referral_user_account, __ = CustomUserAccount.objects.get_or_create(
                    chat_id=custom_user.referral
                )
                top_user, a = TopUser.objects.get_or_create(
                    chat_id=referral_user.chat_id,
                    defaults={
                        'fullname': referral_user.first_name,
                    }
                )
                top_user.balance += int(custom_user_ref_price)
                top_user.weekly_earned += int(custom_user_ref_price)
                top_user.monthly_earned += int(custom_user_ref_price)
                top_user.save()
                referral_user_account.current_price += custom_user_ref_price
                referral_user_account.save()
                if custom_is_premium:
                    referral_user.premium_count += 1
                else:
                    referral_user.invited_count += 1
                custom_user.save()
                bot.send_message(
                    chat_id=referral_user_account.chat_id,
                    text=f"""
🎉 Tabriklaymiz!  Siz taklif qilgan foydalanuvchi ro'yxatdan o'tdi!

Sizga {custom_user_ref_price} so'm bonus berildi.
            """

                )
            except CustomUser.DoesNotExist:
                pass
            bot.send_message(
                chat_id=telegram_id,
                text=(
                    "🎉 Tabriklaymiz! Qurilmangiz muvaffaqiyatli ro'yxatdan o'tdi.\n"
                    "👉 Endi keyingi bosqichga o'tishingiz mumkin."
                ),
                reply_markup=keyword.base()
            )
        return JsonResponse({"status": "ok"}, status=201)

    return JsonResponse({"error": "POST method required"}, status=400)
