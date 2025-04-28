from django.core.management.base import BaseCommand
from app.models import TopUser, CustomUser
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Reset monthly earnings and notify admins'

    def handle(self, *args, **kwargs):
        top_10_users = TopUser.objects.order_by('-monthly_earned')[:10]
        counter = 1
        top_3 = {
            1: '🥇',
            2: '🥈',
            3: '🥉'
        }

        message = "🏆 TOP 10 ta oylik foydalanuvchilar:\n\n"
        for user in top_10_users:
            medal = top_3.get(counter, f"{counter}.")
            username = user.username or f"ID: {user.chat_id}"
            full_link = f'<a href="tg://user?id={user.chat_id}">{username}</a>'
            message += f"{medal} {full_link} - {user.monthly_earned} so'm\n"
            counter += 1

        admins = CustomUser.objects.filter(is_admin=True)

        for admin in admins:
            try:
                response = requests.post(
                    f"https://api.telegram.org/bot{settings.TOKEN}/sendMessage",
                    data={
                        'chat_id': admin.chat_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    }
                )
                if response.status_code != 200:
                    self.stdout.write(
                        self.style.ERROR(f"Xabar yuborilmadi admin {admin.chat_id} uchun: {response.text}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Xato yuz berdi: {str(e)}"))

        TopUser.objects.update(monthly_earned=0)

        self.stdout.write(self.style.SUCCESS('Monthly earnings reset and admins notified successfully.'))
