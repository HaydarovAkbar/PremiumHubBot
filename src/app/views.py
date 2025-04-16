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
from .models import CustomUser, Settings
from telegram import Bot


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
            custom_user.save()
            bot.send_message(
                chat_id=telegram_id,
                text=(
                    "❌ Bu qurilmadan allaqachon boshqa foydalanuvchi foydalanmoqda.\n\n"
                    f"✅ Botdan faqat {bot_settings.device_count} ta qurilmada foydalanish mumkin."
                )
            )
            return JsonResponse({
                "error": "Bu qurilma boshqa foydalanuvchi tomonidan ishlatilgan."
            }, status=403)

        if not (custom_user.device_hash and custom_user.is_active):
            custom_user.device_hash = fingerprint_hash
            custom_user.is_active = True
            custom_user.save()
            bot.send_message(
                chat_id=telegram_id,
                text=(
                    "🎉 Tabriklaymiz! Qurilmangiz muvaffaqiyatli ro'yxatdan o'tdi.\n"
                    "👉 Endi keyingi bosqichga o'tishingiz mumkin."
                )
            )
        return JsonResponse({"status": "ok"}, status=201)

    return JsonResponse({"error": "POST method required"}, status=400)
