from datetime import datetime
import requests
from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts, Group, CustomUserAccount, TopUser, InterestingBonus
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
import requests

keyword = Keyboards()
state = States()
msg = MessageText()


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


def get_bonus_base(update: Update, context: CallbackContext):
    all_channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for channel in all_channel:
        try:
            a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(channel)
        except Exception as e:
            print(e)
    if left_channel:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling)",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        msg = """<b>Bonuslarni qo'lga kiritish uchun shartlar va vazifalar quyidagicha: 👇</b>
        
🔹 Shartlar va talablar bilan tanishib chiqing.
🔹 Ko‘rsatilgan vazifalarni to‘liq bajaring.
🔹 Hammasini to‘g‘ri amalga oshirganingizdan so‘ng bonuslarni qo‘lga kiriting!
        """
        requests.post(
            f"https://api.telegram.org/bot{settings.TOKEN}/sendMessage",
            json={
                "chat_id": user_db.chat_id,
                "text": str(msg),
                "parse_mode": "HTML",
                "reply_markup": keyword.bonus().to_dict(),
                'message_effect_id': "5046509860389126442",  # 5104841245755180586 5046509860389126442
            }
        )
        return state.BONUS


def get_bonus_type(update: Update, context: CallbackContext):
    all_channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for channel in all_channel:
        try:
            a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(channel)
        except Exception as e:
            print(e)
    if left_channel:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        query = update.callback_query
        if query.data == 'back':
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.base())
            return state.START

        elif query.data == 'nik':
            query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            _msg_ = f"""
        <b>O'z telegram ismingizga bizning nomimizni qo'ying va {interesting_bonus.fullname} so'm bonus oling.</b>
        Ustiga bosib nusxalab olishingiz mumkin

        <code>🅿️ PremiumHub</code> 📝
                            """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_NIK
        elif query.data == 'bio':
            query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            _msg_ = f"""
        <b>O'z telegram BIO ingizga bizning nomimizni qo'ying va {interesting_bonus.bio} so'm bonus oling.</b>
        Ustiga bosib nusxalab olishingiz mumkin

        <code>Tg Premium 👇  </code>https://t.me/HubPremiyumBot?start={update.effective_user.id} 📝
                            """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_BIO

        elif query.data == 'premium_bonus':
            user_id = update.effective_user.id
            if not is_premium_user_check(user_id, context.bot.token, user_id):
                query.answer(
                    "📵 Bu tugmani faqatgina premium obunachilar ishlatoladi 📵",
                    show_alert=True
                )
                # _msg = """<b>Bonuslarni qo'lga kiritish uchun shartlar va vazifalar quyidagicha: 👇</b>
                #
                # 🔹 Shartlar va talablar bilan tanishib chiqing.
                # 🔹 Ko‘rsatilgan vazifalarni to‘liq bajaring.
                # 🔹 Hammasini to‘g‘ri amalga oshirganingizdan so‘ng bonuslarni qo‘lga kiriting!"""
                # context.bot.send_message(chat_id=user_id, text=_msg,
                #                          reply_markup=keyword.bonus(),
                #                          parse_mode=ParseMode.HTML
                #                          )
                return state.BONUS
            else:
                query.delete_message()
                reward_db = RewardsChannelBoost.objects.filter(is_active=True).last()
                context.bot.send_photo(chat_id=update.effective_user.id,
                                       photo=msg.channel_boost_id,
                                       caption="<i>Quyidagi tugma orqali ovoz bering va tekshirish tugmasini bosing, har bir boost uchun bonus beriladi</i>",
                                       parse_mode=ParseMode.HTML,
                                       reply_markup=keyword.channel_boost(reward_db.channel_url)
                                       )
                return state.CHANNEL_BOOST_BONUS
        elif query.data == 'stories_bonus':
            story_bonus_price = StoryBonusPrice.objects.filter(is_active=True).last()
            _msg_ = f"<b>👇Pastdaki WEBAPP dan foydalanib storiesingizga video joylang va {story_bonus_price.price} so'm bonus oling.</b>\n\n<code>Eslatib o'tamiz admin tomonidan tekshirilgach vazifa bajarilmagan xolatda akkountingiz BLOK qilinadi va botdan foydalanishingiz taqiqlanadi ❗️</code>"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.story_bonus(settings.STORY_URL)
                                     )
            return state.STORY_BONUS
        elif query.data == 'add_group_bonus':
            query.delete_message()
            group = Group.objects.filter(is_active=True).last()
            if group:
                _msg_ = f"""<b>Quyidagi guruhga do'stlaringiz qo'shing va bonusga ega bo'ling: 👇</b>"""
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text=_msg_,
                                         parse_mode="HTML",
                                         reply_markup=keyword.groups(group)
                                         )
                return state.GROUP_BONUS
            else:
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text="👇 Hozircha bonus uchun guruh kiritilmagan!",
                                         parse_mode="HTML",
                                         reply_markup=keyword.groups(group)
                                         )
        else:
            _msg_ = "<b>Quyidagi qiziqarli vazifalarni bajarib bonuslar oling.</b>"
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_bonus()
                                     )
            return state.INTERESTING_BONUS

    return state.BONUS


def get_user_boosts(chat_id, user_id):
    payload = {
        "chat_id": f'@{chat_id}',  # "@channelusername" yoki integer
        "user_id": user_id
    }
    API_URL = f"https://api.telegram.org/bot{settings.TOKEN}/getUserChatBoosts"
    response = requests.post(API_URL, json=payload)
    if response.ok:
        data = response.json()
        if data.get("ok"):
            return data["result"]['boosts']
    return False


def get_daily_bonus(update: Update, context: CallbackContext):
    all_channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for channel in all_channel:
        try:
            a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(channel)
        except Exception as e:
            print(e)
    if left_channel:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        query = update.callback_query
        if query.data == 'back':
            query.delete_message()
            _msg = """<b>Bonuslarni qo'lga kiritish uchun shartlar va vazifalar quyidagicha: 👇</b>

            🔹 Shartlar va talablar bilan tanishib chiqing.
            🔹 Ko‘rsatilgan vazifalarni to‘liq bajaring.
            🔹 Hammasini to‘g‘ri amalga oshirganingizdan so‘ng bonuslarni qo‘lga kiriting!"""
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.bonus())
            return state.BONUS
        if query.data in ['top_rating',
                                                                                                     'weekly_rating',
                                                                                                     'premium_bonus',
                                                                                                     'stories_bonus',
                                                                                                     'add_group_bonus',
                                                                                                     'nik',
                                                                                                     'bio',
                                                                                                     'daily_bonus',
                                                                                                     'check',
                                                                                                     ]:
            query.delete_message()
            _msg = """<b>Bonuslarni qo'lga kiritish uchun shartlar va vazifalar quyidagicha: 👇</b>

            🔹 Shartlar va talablar bilan tanishib chiqing.
            🔹 Ko‘rsatilgan vazifalarni to‘liq bajaring.
            🔹 Hammasini to‘g‘ri amalga oshirganingizdan so‘ng bonuslarni qo‘lga kiriting!"""
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.bonus())
            return state.BONUS
        # query.delete_message()
        reward_db = RewardsChannelBoost.objects.filter(is_active=True).last()

        def extract_channel_username(url: str) -> str:
            if url.startswith("https://t.me/"):
                return url.rstrip("/").split("/")[-1].strip("@")
            return url.strip("@")

        boost_count = get_user_boosts(extract_channel_username(reward_db.channel_url), update.effective_user.id)
        if not boost_count:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=f"❌ Siz kanalimizga boost bermagansiz xali !)",
                                     reply_markup=keyword.base()
                                     )
            return state.START
        boost_count = len(boost_count)
        daily_bonus, _ = DailyBonus.objects.get_or_create(chat_id=update.effective_user.id, rewards_channel=reward_db)
        if not _:
            # if daily_bonus.count < boost_count:
            #     counter = boost_count - daily_bonus.count
            #     daily_bonus.count = boost_count
            #     daily_bonus.save()
            #     custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
            #     price = counter * int(reward_db.elementary_bonus)
            #     custom_account.current_price += price
            #     custom_account.total_price += price
            #     custom_account.save()
            #     top_user, a = TopUser.objects.get_or_create(
            #         chat_id=update.effective_user.id,
            #         defaults={
            #             'fullname': update.effective_user.full_name,
            #         }
            #     )
            #     top_user.balance += price
            #     top_user.weekly_earned += price
            #     top_user.monthly_earned += price
            #     top_user.save()
            #     context.bot.send_message(chat_id=update.effective_user.id,
            #                              text=f"🎉 Tabriklaymiz sizga {price} so'm kunlik bonus berildi.",
            #                              reply_markup=keyword.base()
            #                              )
            if daily_bonus.last_bonus != datetime.today().date() and boost_count > 0:
                daily_bonus.last_bonus = datetime.today().date()
                daily_bonus.save()
                price = int(reward_db.daily_bonus) * boost_count
                custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
                custom_account.current_price += price
                custom_account.total_price += price
                custom_account.save()
                top_user, a = TopUser.objects.get_or_create(
                    chat_id=update.effective_user.id,
                    defaults={
                        'fullname': update.effective_user.full_name,
                    }
                )
                top_user.balance += price
                top_user.weekly_earned += price
                top_user.monthly_earned += price
                top_user.save()
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text=f"🎉 Tabriklaymiz sizga {price} so'm kunlik bonus berildi.",
                                         reply_markup=keyword.base()
                                         )
            else:
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text="Kunlik bonus allaqachon olgansiz!",
                                         reply_markup=keyword.base()
                                         )
        # else:
        #     # if boost_count == daily_bonus.count
        #     daily_bonus.count = boost_count
        #     daily_bonus.save()
        #     custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
        #     price = boost_count * int(reward_db.elementary_bonus)
        #     custom_account.current_price += price
        #     custom_account.total_price += price
        #     custom_account.save()
        #     top_user, a = TopUser.objects.get_or_create(
        #         chat_id=update.effective_user.id,
        #         defaults={
        #             'fullname': update.effective_user.full_name,
        #         }
        #     )
        #     top_user.balance += price
        #     top_user.weekly_earned += price
        #     top_user.monthly_earned += price
        #     top_user.save()
        #     context.bot.send_message(chat_id=update.effective_user.id,
        #                              text=f"🎉 Tabriklaymiz sizga {price} so'm kanalimizga ovoz berganingiz uchun bonus berildi.",
        #                              reply_markup=keyword.base()
        #                              )
        #     return state.START
    return state.BONUS


def get_stories_bonus(update: Update, context: CallbackContext):
    all_channel = Channel.objects.filter(is_active=True)
    left_channel = []
    for channel in all_channel:
        try:
            a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
            if a.status == 'left':
                left_channel.append(channel)
        except Exception as e:
            print(e)
    if left_channel:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling",
                                 reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        query = update.callback_query
        if query.data == 'back':
            query.delete_message()
            _msg = """<b>Bonuslarni qo'lga kiritish uchun shartlar va vazifalar quyidagicha: 👇</b>

            🔹 Shartlar va talablar bilan tanishib chiqing.
            🔹 Ko‘rsatilgan vazifalarni to‘liq bajaring.
            🔹 Hammasini to‘g‘ri amalga oshirganingizdan so‘ng bonuslarni qo‘lga kiriting!"""
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.bonus())
            return state.BONUS
        query.delete_message()
        story_db = StoryBonusPrice.objects.filter(is_active=True).last()
        story_bonus = StoryBonusAccounts.objects.filter(chat_id=update.effective_user.id)
        if story_bonus.exists():
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Siz allaqachon bonus olgansiz!",
                                     reply_markup=keyword.base()
                                     )
            return state.STORY_BONUS
        stories_counter = context.chat_data.get('stories_counter', 0)
        context.chat_data['stories_counter'] = stories_counter + 1
        if context.chat_data['stories_counter'] > 3:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.bonus()
                                     )
            custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
            custom_account.current_price += story_db.price
            custom_account.save()
            top_user, a = TopUser.objects.get_or_create(
                chat_id=update.effective_user.id,
                defaults={
                    'fullname': update.effective_user.full_name,
                }
            )
            top_user.balance += int(story_db.price)
            top_user.weekly_earned += int(story_db.price)
            top_user.monthly_earned += int(story_db.price)
            top_user.save()
            StoryBonusAccounts.objects.create(chat_id=update.effective_user.id)
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=f"🎉 Tabriklaymiz sizga {story_db.price} so'm kanalimizga ovoz berganingiz uchun bonus berildi.",
                                     )
        else:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Tekshirilmoqda iltimos keyinroq urinib ko'ring 🕞",
                                     reply_markup=keyword.story_bonus(settings.STORY_URL)
                                     )
        return state.STORY_BONUS
    return state.BONUS
