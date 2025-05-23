import time
# import pymysql
from django.core.management.base import BaseCommand
from app.models import CustomUser, CustomUserAccount  # o'z model yo'lingni tekshir!


class Command(BaseCommand):
    help = "Migrate users from external MySQL database (MariaDB) to Django DB"

    def handle(self, *args, **options):
        # host = "109.73.201.204"
        # user = "premium_bot"
        # password = "Shohzod1009"
        # database = "premium_bot"

        # batch_size = 1000
        # offset = 57000
        # total_imported = 0
        # import re
        # while True:
        #     try:
        #         connection = pymysql.connect(
        #             host=host,
        #             user=user,
        #             password=password,
        #             database=database
        #         )
        #         with connection.cursor() as cursor:
        #             query = f"SELECT * FROM users LIMIT {batch_size} OFFSET {offset}"
        #             cursor.execute(query)
        #             rows = cursor.fetchall()
        #
        #         connection.close()
        #
        #         if not rows:
        #             self.stdout.write(self.style.SUCCESS("✅ Barcha foydalanuvchilar import qilindi."))
        #             break
        #
        #         self.stdout.write(f"📦 {len(rows)} ta foydalanuvchi import qilinmoqda (offset={offset})...")
        #
        #         for row in rows:
        #             is_blocked = row[3] == 'true'
        #             phone_number = row[10] if len(row) > 10 else ""
        #             referral_raw = row[5] if len(row) > 5 and row[5] is not None else ''
        #             if referral_raw:
        #                 match = re.search(r'\d+', str(referral_raw))
        #                 if match:
        #                     group = match.group()
        #                     if group and group.isdigit():
        #                         referral = int(group)
        #
        #             custom_user, _ = CustomUser.objects.get_or_create(
        #                 chat_id=row[1],
        #                 defaults={
        #                     'is_blocked': is_blocked,
        #                     'phone_number': phone_number,
        #                     'is_active': False,
        #                     'referral': referral,
        #                 }
        #             )
        #
        #             custom_user_account, __ = CustomUserAccount.objects.get_or_create(
        #                 chat_id=row[1],
        #                 defaults={
        #                     'current_price': row[4] if row[4] is not None else 0,
        #                     'total_price': row[4] if row[4] is not None else 0,
        #                 }
        #             )
        #
        #             total_imported += 1
        #             time.sleep(0.01)  # juda tez bo'lsa timeout bo'lishi mumkin
        #
        #         offset += batch_size
        #
        #     except Exception as e:
        #         self.stderr.write(f"❌ Xatolik: {e}")
        #         break

        # self.stdout.write(self.style.SUCCESS(f"🎉 Jami {total_imported} foydalanuvchi import qilindi!"))
        # connection = pymysql.connect(
        #     host=host,
        #     user=user,
        #     password=password,
        #     database=database
        # )
        # with connection.cursor() as cursor:
        #     query = f"-- SELECT * FROM users LIMIT 5 OFFSET 10"
        #     query = f"SELECT * FROM users_trans;"
        #     cursor.execute(query)
        #     rows = cursor.fetchall()
        #
        # connection.close()
        #
        # # if not rows:
        # #     self.stdout.write(self.style.SUCCESS("✅ Barcha foydalanuvchilar import qilindi."))
        # print(rows)
        counter = 0
        print("Migrating users from external MySQL database...")
        user_6283303160 = CustomUser.objects.filter(referral=6283303160)
        for user in user_6283303160:
            print(f"CHAT ID: {user.chat_id}, PHONE: {user.phone_number}")
        print(f"Count users: {user_6283303160.count()}")
        # for cus_user in CustomUser.objects.all():
        #     referral_count = CustomUser.objects.filter(referral=cus_user.chat_id).count()
        #     print("User: {}, referral: {}".format(cus_user.chat_id, referral_count))
        # if referral_count > 0:
        #     cus_user.invited_count = referral_count
        #     cus_user.save()
        # counter += 1
        #
        # if counter % 100 == 0:
        #     time.sleep(1)
        #     print("Migrated {} users".format(counter))

        print("End!")
