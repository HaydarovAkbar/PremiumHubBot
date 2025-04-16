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
from .models import CustomUser


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
        tur = data.get("tur")
        width = str(data.get("width"))
        height = str(data.get("height"))
        til = data.get("til")
        hotira = str(data.get("hotira"))
        telegram_id = int(data.get("telegram_id"))
        print("-------> chatid", telegram_id)
        # Qurilma fingerprintini yasash (hash qilish)
        raw_string = model + tur + width + height + til + hotira
        fingerprint_hash = hashlib.sha256(raw_string.encode()).hexdigest()
        print(CustomUser.objects.filter(chat_id=telegram_id).count())
        # Tekshirish: boshqa user shu qurilmadan foydalanayotgan bo‘lsa
        existing = CustomUser.objects.filter(
            device_hash=fingerprint_hash
        ).exclude(chat_id=telegram_id).first()

        if existing:
            return JsonResponse({
                "error": "Bu qurilma boshqa foydalanuvchi tomonidan ishlatilgan."
            }, status=403)

        # Agar mavjud bo'lmasa, saqlash yoki mavjudiga qaytish
        CustomUser.objects.get_or_create(
            device_hash=fingerprint_hash,
            chat_id=telegram_id
        )

        return JsonResponse({"status": "ok"}, status=201)

    return JsonResponse({"error": "POST method required"}, status=400)
