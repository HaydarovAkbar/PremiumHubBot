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
from .models import CustomUser, Settings, CustomUserAccount, TopUser, DailyBonus, RewardsChannelBoost, Group, \
    InvitedUser, InvitedBonusUser
# from telegram import Bot
from .bot.keyboards.base import Keyboards
from django.conf import settings
import requests
from datetime import datetime, timedelta
from collections import defaultdict


def is_premium_user_check(user_id: int, bot_token: str, chat_id: int) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
    response = requests.get(url, params={
        "chat_id": chat_id,
        "user_id": user_id
    })

    if response.status_code == 200:
        data = response.json()
        return data.get("result", {}).get("user", {}).get("is_premium", False)
    return False

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
            if "chat_boost" in body_json:
                boost_data = body_json["chat_boost"]
                user_id = boost_data["boost"]["source"]["user"]["id"]
                reward_db = RewardsChannelBoost.objects.filter(is_active=True).last()
                daily_bonus, _ = DailyBonus.objects.get_or_create(chat_id=user_id,
                                                                  rewards_channel=reward_db)
                custom_user = CustomUser.objects.get(chat_id=user_id)
                fullname = f"{custom_user.first_name} {custom_user.last_name}"
                daily_bonus.count = 1 + daily_bonus.count if daily_bonus.count else 0
                daily_bonus.save()
                custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=user_id)
                price = 1 * reward_db.elementary_bonus
                custom_account.current_price = price + custom_account.current_price if custom_account.current_price else 0
                custom_account.total_price = price + custom_account.total_price if custom_account.total_price else 0
                custom_account.save()
                top_user, a = TopUser.objects.get_or_create(
                    chat_id=user_id,
                    defaults={
                        'fullname': fullname,
                    }
                )
                top_user.balance = price + top_user.balance if top_user.balance else 0
                top_user.weekly_earned = price + top_user.weekly_earned if top_user.weekly_earned else 0
                top_user.monthly_earned = price + top_user.monthly_earned if top_user.monthly_earned else 0
                top_user.save()
                bot.send_message(chat_id=user_id,
                                 text=f"🎉 Tabriklaymiz sizga {price} 💎 kunlik bonus berildi.",
                                 # reply_markup=keyword.base()
                                 )
            elif "message" in body_json and "new_chat_members" in body_json["message"]:
                update: Update = Update.de_json(body_json, bot)
                message = update.message

                new_members = message.new_chat_members

                inviter = message.from_user

                last_group = Group.objects.filter(is_active=True).last()
                if not last_group:
                    return HttpResponse('No active group')

                current_invite_count = InvitedUser.objects.filter(
                    inviter_chat_id=inviter.id,
                    group=last_group
                ).count()

                if current_invite_count >= last_group.limit:
                    return HttpResponse('Limit reached, bonus berilmaydi')

                for new_user in new_members:
                    if not new_user.is_bot and new_user.id != inviter.id:
                        invite_db, created = InvitedUser.objects.get_or_create(
                            new_user_chat_id=new_user.id,
                            inviter_chat_id=inviter.id,
                            group=last_group
                        )

                        if created:
                            current_invite_count += 1

                            if current_invite_count <= last_group.limit:
                                plus_balance = int(last_group.price)

                                user_acc, _ = CustomUserAccount.objects.get_or_create(chat_id=inviter.id)
                                user_acc.current_price += plus_balance
                                user_acc.total_price += plus_balance
                                user_acc.save()

                                top_user, _ = TopUser.objects.get_or_create(
                                    chat_id=inviter.id,
                                    defaults={'fullname': inviter.full_name}
                                )
                                top_user.balance += plus_balance
                                top_user.weekly_earned += plus_balance
                                top_user.monthly_earned += plus_balance
                                top_user.save()

                                InvitedBonusUser.objects.get_or_create(chat_id=inviter.id, group=last_group)

                                bot.send_message(
                                    chat_id=inviter.id,
                                    text=f"🎉 Siz {new_user.full_name} ni guruhga qo‘shganingiz uchun {plus_balance} 💎 bonus oldingiz!",
                                    parse_mode="HTML"
                                )
                            else:
                                print(f"Limitdan oshib ketdi: {inviter.id}")
            else:
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
                    "<b>Siz allaqachon boshqa profillaringiz orqali botimizdan foydalanmoqdasiz.</b>\n"
                    f"Ushbu sababdan profilingiz botimizda blocklanadi.\n\n"
                    "👨‍💻Agar buni xato deb hisoblasangiz @hup_support ga murojaat qiling."
                ),
                parse_mode='HTML'
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

            if custom_user.id < 95000:
                return JsonResponse({"status": "ok"}, status=201)

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
                top_user.balance += custom_user_ref_price
                top_user.weekly_earned += custom_user_ref_price
                top_user.monthly_earned += custom_user_ref_price
                top_user.save()
                referral_user_account.current_price += custom_user_ref_price
                referral_user_account.save()
                if custom_is_premium:
                    referral_user.premium_count += 1
                else:
                    referral_user.invited_count += 1
                referral_user.save()
                custom_user.save()
                fullname = f"{custom_user.first_name if custom_user.first_name else '-'} {custom_user.last_name if custom_user.last_name else '-'}"
                minio = f"<a href='tg://user?id={custom_user.chat_id}'>{fullname}</a>"
                bot.send_message(
                    chat_id=referral_user_account.chat_id,
                    text=f"""
<b>🎉 Tabriklaymiz!  Siz {minio} ni taklif qilgan foydalanuvchi ro'yxatdan o'tdi va sizga {custom_user_ref_price} 💎 bonus berildi.</b>
            """, parse_mode="HTML"
                )
            except Exception:
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


def user_stats_view(request):
    last_month = datetime.today() - timedelta(days=31)
    start_date = last_month
    today = datetime.today().date()
    days = (today - start_date.date()).days + 1

    daily_data = []
    max_added = 0
    max_blocked = 0

    for i in range(days):
        day = (start_date + timedelta(days=i)).date()
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())

        added_count = CustomUser.objects.filter(created_at__range=(day_start, day_end), is_active=True).count()
        blocked_count = CustomUser.objects.filter(is_blocked=True, created_at__range=(day_start, day_end)).count()

        max_added = max(max_added, added_count)
        max_blocked = max(max_blocked, blocked_count)

        daily_data.append({
            'date': day.strftime('%d-%m'),
            'added': added_count,
            'blocked': blocked_count
        })

    for item in daily_data:
        item['added_percent'] = round((item['added'] / max_added) * 100, 1) if max_added > 0 else 0
        item['blocked_percent'] = round((item['blocked'] / max_blocked) * 100, 1) if max_blocked > 0 else 0

    return render(request, 'user_stats.html', {'daily_data': daily_data[::-1]})
