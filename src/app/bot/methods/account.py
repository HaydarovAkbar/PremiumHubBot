from datetime import datetime

from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts, Group, CustomUserAccount, InvitedUser, Settings, SpendPrice, SpendPriceField, PromoCodes, \
    InterestingBonus, TopUser, InvitedBonusUser, InterestingBonusUser, CustomPromoCode, CustomUserPromoCode

from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
from django.utils.timezone import timedelta
from .bonus import settings, get_user_boosts, is_premium_user_check
import random
from django.utils import timezone

keyword = Keyboards()
state = States()
msg = MessageText()


def promo_code_generator():
    fields = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
        'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
        's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
        'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
    ]
    promo_code = ''.join(random.choice(fields) for _ in range(10))
    return promo_code


def my_account(update: Update, context: CallbackContext):
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
        context.bot.send_photo(chat_id=update.effective_user.id,
                               photo='AgACAgIAAxkBAAEaMCdoeJzgVCgsP05l79z72EpYtLSnfAACB_oxG14bwUsodGhV1zrgcAEAAwIAA3kAAzYE',
                               caption="Botni ishga tushirish uchun quyidagi kanallarga obuna bo’ling va “♻️ Tekshirish” tugmasini bosing",
                               reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id,
                                                             defaults={
                                                                 'current_price': 0.0,
                                                                 'total_price': 0.0,
                                                             }
                                                             )
        group_added_count = InvitedUser.objects.filter(inviter_chat_id=update.effective_user.id).count()
        from django.utils.timezone import now

        # Joriy haftaning boshidan boshlab taklif qilingan do‘stlar
        start_of_week = now().date() - timedelta(days=now().weekday())  # dushanba
        referrals_this_week = CustomUser.objects.filter(
            referral=user_db.chat_id,
            created_at__date__gte=start_of_week,
            is_active=True,
        ).count()

        _msg = f"""
✨ <b>Profile</b>
_________________
👤<b> Ism:</b> {update.effective_chat.full_name}
🆔<b> ID:</b> {update.effective_user.id}
_________________
💰<b> Balans:</b> {account.current_price} 💎
👥<b> Referral:</b> {user_db.invited_count + user_db.premium_count}
📅<b> Joriy haftada:</b> {referrals_this_week}
📣<b> Guruhga taklif qilganlar:</b> {group_added_count}
_________________
"""
        update.message.reply_photo(
            photo=msg.my_profile_id,
            caption=_msg,
            parse_mode=ParseMode.HTML,
            reply_markup=keyword.my_account(),
        )
        # update.message.reply_text(_msg,
        #                           # photo=msg.my_profile_id,
        #                           # caption=_msg,
        #                           parse_mode=ParseMode.HTML,
        #                           reply_markup=keyword.my_account(),
        #                           )
        return state.START


def universal_callback_data(update: Update, context: CallbackContext):
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
        context.bot.send_photo(chat_id=update.effective_user.id,
                               photo='AgACAgIAAxkBAAEaMCdoeJzgVCgsP05l79z72EpYtLSnfAACB_oxG14bwUsodGhV1zrgcAEAAwIAA3kAAzYE',
                               caption="Botni ishga tushirish uchun quyidagi kanallarga obuna bo’ling va “♻️ Tekshirish” tugmasini bosing",
                               reply_markup=keyword.channels(left_channel))
        return state.CHECK_CHANNEL
    user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
    if user_db.is_active:
        query = update.callback_query
        account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id, )
        if query.data == 'back':
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.base())
            return state.START
        elif query.data == 'send_admin':
            query.answer()
            promo_code = context.chat_data['promo_code']
            promo_db = PromoCodes.objects.get(name=promo_code)
            spent_field = SpendPriceField.objects.get(name=promo_db.reward)
            try:
                adm_msg = (
                    f"#{promo_db.id}\n"
                    f"<b>🆕 Yangi promo kod ro'yxatdan o'tdi!\n\n</b>"
                    f"🔹 Promo kod: <code>{promo_code}</code>\n"
                    f"🔹 Promo turi: <code>{spent_field.name}</code>\n"
                    f"🔹 Promo narxi: <code>{spent_field.price}</code>\n"
                    f"🔹 Foydalanuvchi: <a href='tg://user?id={user_db.chat_id}'>{update.effective_chat.full_name}</a>\n"
                    f"🔹 User ID: <code>{user_db.chat_id}</code>\n"
                    f"📅 DATE: {datetime.now()}\n"
                )
                context.bot.send_message(chat_id=-1002275382452,  # -1002275382452,
                                         text=adm_msg,
                                         parse_mode='HTML',
                                         )
            except Exception as e:
                context.bot.send_message(chat_id=-1002275382452,
                                         text=str(e),
                                         parse_mode='HTML',
                                         )
            _msg_ = f"""
        <b>✅ Promokod adminga muvafaqiyatli yuborildi!</b>
    
        Tez orada xaridingiz tasdiqlanadi va amalga oshiriladi!!!
        Iltimos biroz sabr qiling.
        """
            # query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.base())
            return state.START
        elif query.data == 'add_custom_promo':
            query.answer()
            query.delete_message()
            context.bot.send_message(
                chat_id=update.effective_user.id,
                text="Promo kodni yuboring:",
            )
            return state.CHECK_PROMO

        elif query.data == 'get_promo_code':
            spend_field = SpendPriceField.objects.get(id=context.chat_data['promo_code'])
            user_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
            user_account.current_price -= spend_field.price
            user_account.save()
            promo_code = promo_code_generator()
            PromoCodes.objects.create(
                chat_id=update.effective_user.id,
                name=promo_code,
                status=True,
                reward=spend_field.name[:50],
            )
            _msg_ = f"""
Sizga <b>{spend_field.name}</b> uchun promokod berildi

Sizning promokod 👉 <code>{promo_code}</code>
Narxi: <b>{spend_field.price} 💎 </b>

Ushbu promokodni adminga yuboring.
Admin sizga taklif doirasidagi xizmatni faollashtiradi.
            """
            context.chat_data['promo_code'] = promo_code
            query.edit_message_text(
                _msg_,
                parse_mode=ParseMode.HTML,
                reply_markup=keyword.admin_send_url('hup_support '),
            )
            promo_code = context.chat_data['promo_code']
            promo_db = PromoCodes.objects.get(name=promo_code)
            spent_field = SpendPriceField.objects.get(name=promo_db.reward)
            try:
                adm_msg = (
                    f"#{promo_db.id}\n"
                    f"<b>🆕 Yangi promo kod ro'yxatdan o'tdi!\n\n</b>"
                    f"🔹 Promo kod: <code>{promo_code}</code>\n"
                    f"🔹 Promo turi: <code>{spent_field.name}</code>\n"
                    f"🔹 Promo narxi: <code>{spent_field.price}</code>\n"
                    f"🔹 Foydalanuvchi: <a href='tg://user?id={user_db.chat_id}'>{update.effective_chat.full_name}</a>\n"
                    f"🔹 User ID: <code>{user_db.chat_id}</code>\n"
                    f"📅 DATE: {datetime.now()}\n"
                )
                context.bot.send_message(chat_id=-1002275382452,  # -1002275382452,
                                         text=adm_msg,
                                         parse_mode='HTML',
                                         )
            except Exception as e:
                context.bot.send_message(chat_id=-1002275382452,
                                         text=str(e),
                                         parse_mode='HTML',
                                         )
            return state.SEND_PROMO_CODE

        elif query.data == 'spend':
            from django.utils.timezone import now

            account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
            settings_bot = Settings.objects.filter(is_active=True).last()
            user = CustomUser.objects.filter(chat_id=update.effective_user.id).first()

            if not user:
                update.callback_query.answer("Foydalanuvchi topilmadi!", show_alert=True)
                return state.START

            # Joriy haftaning boshidan boshlab taklif qilingan do‘stlar
            start_of_week = now().date() - timedelta(days=now().weekday())  # dushanba
            referrals_this_week = CustomUser.objects.filter(
                referral=user.chat_id,
                created_at__date__gte=start_of_week
            ).count()

            required_referrals = int(settings_bot.spend_price)

            if referrals_this_week >= required_referrals:
                last_spend_price = SpendPrice.objects.filter(is_active=True).last()
                if last_spend_price:
                    fields = SpendPriceField.objects.filter(spend_price=last_spend_price)
                    update.callback_query.delete_message()
                    context.bot.send_photo(
                        photo=msg.gift_photo_id,
                        chat_id=update.effective_user.id,
                        caption=last_spend_price.text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyword.spend_fields(fields, account.current_price),
                    )
                    return state.MY_ACCOUNT

                update.callback_query.answer(
                    f"Kechirasiz xizmat hali to'liq ishga tushmagan !",
                )
            else:
                update.callback_query.answer(
                    f"Bu xizmatdan foydalanish uchun joriy haftada kamida {required_referrals} ta do‘stingizni taklif qilishingiz kerak.\n\n"
                    f"Siz taklif qilganlar: {referrals_this_week} ta",
                    show_alert=True,
                )

            return state.START

        elif query.data == 'nik':
            query.answer()
            query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            _msg_ = f"""
<b>O'z telegram ismingiz oldiga bizning nomimizni qo'ying va {interesting_bonus.fullname} 💎 bonus oling.</b>
Ustiga bosib nusxalab olishingiz mumkin

<code>🅿️ PremiumHub</code> 📝
                            """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_NIK
        elif query.data == 'nik_check':
            query.answer()
            # query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            interesting_bonus_user, _ = InterestingBonusUser.objects.get_or_create(
                chat_id=update.effective_user.id
            )
            user_full_name = update.effective_chat.full_name
            required_text = "PremiumHub"
            has_in_name = required_text.lower() in user_full_name.lower()
            if has_in_name:
                user_account = CustomUserAccount.objects.get(
                    chat_id=update.effective_user.id,
                )
                if interesting_bonus_user.fullname:
                    _msg_ = "<b>Siz allaqachon bu bonusni olgansiz!</b>"
                    query.delete_message()
                    context.bot.send_message(chat_id=update.effective_user.id,
                                             text=_msg_,
                                             parse_mode="HTML",
                                             reply_markup=keyword.bonus()
                                             )
                    return state.INTERESTING_BONUS
                bonus_amount = interesting_bonus.fullname
                user_account.current_price += bonus_amount
                user_account.total_price += bonus_amount
                user_account.save()
                top_user, a = TopUser.objects.get_or_create(
                    chat_id=update.effective_user.id,
                    defaults={
                        'fullname': update.effective_user.full_name,
                    }
                )
                top_user.balance += bonus_amount
                top_user.weekly_earned += bonus_amount
                top_user.fullname = update.effective_user.full_name
                top_user.monthly_earned += bonus_amount
                top_user.save()
                interesting_bonus_user.fullname = True
                interesting_bonus_user.save()
                _msg_ = f"""✅ Tabriklaymiz! Siz {bonus_amount} 💎 bonus qo'lga kiritdingiz."""
                context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=_msg_,
                    parse_mode="HTML"
                )
                return state.INTERESTING_BONUS_NIK
            _msg_ = f"<b>❗️ Kechirasiz tekshirish natijasida sizda talabga javob beradigan nikname aniqlanmadi</b>"
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML", )
            # reply_markup=keyword.interesting_check_bonus())
            return state.INTERESTING_BONUS_NIK
        elif query.data == 'bio':
            query.answer()
            query.delete_message()
            interesting_bonus = InterestingBonus.objects.filter().last()
            _msg_ = f"""
<b>O'z telegram BIO ingizga bizning nomimizni qo'ying va {interesting_bonus.bio} 💎 bonus oling.</b>
Ustiga bosib nusxalab olishingiz mumkin

<code>Tg Premium 👇 https://t.me/HubPremiyumBot?start={update.effective_user.id} </code>📝
                            """
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML",
                                     reply_markup=keyword.interesting_check_biobonus())
            return state.INTERESTING_BONUS_BIO
        elif query.data == 'top_rating':
            query.answer(text="Iltimos kuting... 🔄")
            _msg_ = "🏆TOP 20 ta foydalanuvchilar:\n\n"
            top_20_user = CustomUserAccount.objects.order_by('-current_price')[:20]
            counter = 1
            top_3 = {
                '1': '🥇',
                '2': '🥈',
                '3': '🥉'
            }
            for user in top_20_user:
                medal = top_3.get(str(counter), counter)
                top_us = TopUser.objects.filter(chat_id=user.chat_id)
                cus = CustomUser.objects.get(chat_id=user.chat_id)
                fullname = cus.first_name if cus.first_name else ' - '
                fullname += cus.last_name if cus.last_name else ' - '
                if top_us.exists():
                    fullname = top_us.first().fullname
                _msg_ += f"{medal}. {fullname} - {user.current_price} 💎\n"
                counter += 1
            # query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     # reply_markup=keyword.back()
                                     )
        elif query.data == 'weekly_rating':
            query.answer(text="Iltimos kuting... 🔄")
            _msg_ = "🏆TOP 10 ta haftalik foydalanuvchilar:\n\n"
            top_20_user = TopUser.objects.order_by('-weekly_earned')[:10]
            counter = 1
            top_3 = {
                '1': '🥇',
                '2': '🥈',
                '3': '🥉'
            }
            for user in top_20_user:
                medal = top_3.get(str(counter), counter)
                _msg_ += f"{medal}. {user.fullname} - {user.monthly_earned} 💎\n"
                counter += 1
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     )
        elif query.data == 'bio_check':
            query.answer()
            interesting_bonus = InterestingBonus.objects.filter().last()
            interesting_bonus_user, _ = InterestingBonusUser.objects.get_or_create(
                chat_id=update.effective_user.id
            )
            chat_info = context.bot.get_chat(update.effective_user.id)
            user_bio = chat_info.bio
            required_text = f"Tg Premium 👇 https://t.me/{settings.USERNAME}?start={update.effective_user.id}"
            has_in_name = required_text.lower() in user_bio.lower()

            if has_in_name:
                query.delete_message()
                user_account = CustomUserAccount.objects.get(
                    chat_id=update.effective_user.id,
                )
                if interesting_bonus_user.bio:
                    _msg_ = "<b>Siz allaqachon bu bonusni olgansiz!</b>"
                    query.delete_message()
                    context.bot.send_message(chat_id=update.effective_user.id,
                                             text=_msg_,
                                             parse_mode="HTML",
                                             reply_markup=keyword.bonus()
                                             )
                    return state.INTERESTING_BONUS
                bonus_amount = interesting_bonus.bio
                user_account.current_price += bonus_amount
                user_account.total_price += bonus_amount
                user_account.save()
                top_user, a = TopUser.objects.get_or_create(
                    chat_id=update.effective_user.id,
                    defaults={
                        'fullname': update.effective_user.full_name,
                    }
                )
                top_user.balance += bonus_amount
                top_user.weekly_earned += bonus_amount
                top_user.fullname = update.effective_user.full_name
                top_user.monthly_earned += bonus_amount
                top_user.save()
                interesting_bonus_user.bio = True
                interesting_bonus_user.save()
                _msg_ = f"""✅ Tabriklaymiz! Siz {bonus_amount} 💎 bonus qo'lga kiritdingiz."""
                context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=_msg_,
                    parse_mode="HTML"
                )
                return state.INTERESTING_BONUS_BIO
            _msg_ = f"<b>❗️ Kechirasiz tekshirish natijasida sizda talabga javob beradigan bio aniqlanmadi</b>"
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode="HTML", )
            return state.INTERESTING_BONUS_BIO
        elif query.data == 'premium_bonus':
            user_id = update.effective_user.id
            if not is_premium_user_check(user_id, context.bot.token, user_id):
                query.answer(
                    "📵 Bu tugmani faqatgina premium obunachilar ishlatoladi 📵",
                    show_alert=True
                )
                return state.BONUS
            else:
                query.answer()
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
            query.answer()
            story_bonus_price = StoryBonusPrice.objects.filter(is_active=True).last()
            _msg_ = (
                f"<b>👇Pastdaki WEBAPP dan foydalanib storiesingizga video joylang va {story_bonus_price.price} 💎 bonus oling.</b>\n\n"
                f"<code>Eslatib o'tamiz barchasi tekshiriladi vazifa bajarilganidan so'ng sizga Bonus taqdim qilinadi ❗️</code>")
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=_msg_,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=keyword.story_bonus(settings.STORY_URL)
                                     )
            return state.STORY_BONUS
        elif query.data == 'add_group_bonus':
            # query.answer()
            # query.delete_message()
            # group = Group.objects.filter(is_active=True).last()
            # if group:
            #     _msg_ = f"""<b>Quyidagi guruhga do'stlaringiz qo'shing va bonusga ega bo'ling: 👇</b>"""
            #     context.bot.send_message(chat_id=update.effective_user.id,
            #                              text=_msg_,
            #                              parse_mode="HTML",
            #                              reply_markup=keyword.groups(group)
            #                              )
            #     return state.GROUP_BONUS
            # else:
            #     context.bot.send_message(chat_id=update.effective_user.id,
            #                              text="👇 Hozircha bonus uchun guruh kiritilmagan!",
            #                              parse_mode="HTML",
            #                              reply_markup=keyword.groups(group)
            #                              )
            query.answer("Bu bo'lim vaqtinchalik ishlamayabdi tez orada tuzatiladi", show_alert=True)
        elif query.data == 'group_check':
            query.answer()
            query.delete_message()
            last_group = Group.objects.filter(is_active=True).last()
            if last_group:
                invited_count = InvitedUser.objects.filter(
                    inviter_chat_id=update.effective_user.id,
                    group=last_group,
                    # is_active=False
                )
                if invited_count.count() <= last_group.limit:
                    user_account, _ = CustomUserAccount.objects.get_or_create(
                        chat_id=update.effective_user.id,
                    )
                    invited_c = InvitedUser.objects.filter(
                        inviter_chat_id=update.effective_user.id,
                        group=last_group,
                        is_active=False
                    )
                    invited_bonus_user = InvitedBonusUser.objects.get_or_create(
                        chat_id=update.effective_user.id,
                        group=last_group,
                    )
                    if invited_bonus_user.clean or invited_c.count() == 0:
                        context.bot.send_message(chat_id=update.effective_user.id,
                                                 text="<b>Siz allaqachon bu guruhga odam qo'shib bonus olgansiz ❗️</b>",
                                                 parse_mode=ParseMode.HTML,
                                                 )
                    else:
                        plus_balance = last_group.price * invited_c.count()
                        user_account.current_price += plus_balance
                        user_account.total_price += plus_balance
                        invited_c.update(is_active=True)
                        invited_c.save()
                        user_account.save()
                        top_user, a = TopUser.objects.get_or_create(
                            chat_id=update.effective_user.id,
                            defaults={
                                'fullname': update.effective_user.full_name,
                            }
                        )
                        top_user.balance += plus_balance
                        top_user.weekly_earned += plus_balance
                        top_user.fullname = update.effective_user.full_name
                        top_user.monthly_earned += plus_balance
                        top_user.save()
                        invited_bonus_user.clean = True
                        invited_bonus_user.save()
                        context.bot.send_message(chat_id=update.effective_user.id,
                                                 text="<b>🎉 Tabriklaymiz!</b>\n\n"
                                                      f"Siz guruhga yangi a'zolarni muvaffaqiyatli qo‘shdingiz va buning evaziga {plus_balance} 💎 ga ega bo‘ldingiz! 🔥\n\n"
                                                      "Doimiy ishtirok eting va yanada ko‘proq odamlarni qo‘shing — keyingi bonuslar sizni kutmoqda! 💰\n"
                                                      "Har bir faol harakatingiz uchun sizni mukofotlar bilan rag‘batlantiramiz! 🏆",
                                                 parse_mode="HTML"
                                                 )
            else:
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text="<b>👇 Hozircha bonus uchun guruh kiritilmagan ❗️</b>",
                                         parse_mode=ParseMode.HTML,
                                         )
            return state.GROUP_BONUS

        elif query.data == 'story_check':
            # query.delete_message()
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
                query.answer()
                query.delete_message()
                custom_account, __ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
                custom_account.current_price += story_db.price
                custom_account.save()
                top_user, a = TopUser.objects.get_or_create(
                    chat_id=update.effective_user.id,
                    defaults={
                        'fullname': update.effective_user.full_name,
                    }
                )
                if not a:
                    top_user.fullname = update.effective_user.full_name
                    top_user.save()
                top_user.balance += story_db.price
                top_user.weekly_earned += story_db.price
                top_user.fullname = update.effective_user.full_name
                top_user.monthly_earned += story_db.price
                top_user.save()
                StoryBonusAccounts.objects.create(chat_id=update.effective_user.id)
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text=f"🎉 Tabriklaymiz sizga {story_db.price} 💎 kanalimizga ovoz berganingiz uchun bonus berildi.",
                                         # reply_markup=keyword.bonus()
                                         )
            else:
                query.answer("Tekshirilmoqda iltimos keyinroq urinib ko'ring 🕞", show_alert=True)
            return state.STORY_BONUS

        elif query.data == 'daily_bonus':
            query.answer()
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
            daily_bonus, _ = DailyBonus.objects.get_or_create(chat_id=update.effective_user.id,
                                                              rewards_channel=reward_db)
            if not _:
                if daily_bonus.last_bonus != datetime.today().date() and boost_count > 0:
                    daily_bonus.last_bonus = datetime.today().date()
                    daily_bonus.save()
                    price = reward_db.daily_bonus * boost_count
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
                    top_user.fullname = update.effective_user.full_name
                    top_user.weekly_earned += price
                    top_user.monthly_earned += price
                    top_user.save()
                    context.bot.send_message(chat_id=update.effective_user.id,
                                             text=f"🎉 Tabriklaymiz sizga {price} 💎 kunlik bonus berildi.",
                                             reply_markup=keyword.base()
                                             )
                else:
                    context.bot.send_message(chat_id=update.effective_user.id,
                                             text="Kunlik bonus allaqachon olgansiz!",
                                             reply_markup=keyword.base()
                                             )
            return state.BONUS

        else:
            now = timezone.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            spend_field = SpendPriceField.objects.get(id=query.data)
            bot_setting = Settings.objects.filter(is_active=True).last()
            user_promo_count = PromoCodes.objects.filter(chat_id=user_db.chat_id,
                                                         created_at__gte=start_of_month,
                                                         created_at__lte=now
                                                         ).count()
            if account.current_price >= spend_field.price and bot_setting.promo_limit > user_promo_count:
                query.answer()
                context.chat_data['promo_code'] = query.data
                query.delete_message()
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text=f"""
                <b>🎉 Siz ushbu taklifdan foydalana olasiz!</b>

                Promokod olish tugmasini bosing,
                hisobingizdan {spend_field.price} 💎 yechiladi va
                sizga promokod beriladi.
                """,
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=keyword.get_promo_code(),
                                         )
                return state.GET_PROMO_CODE
            else:
                if spend_field.price >= account.current_price:
                    query.answer(
                        f"""
                        Ush bu taklifdan foydalanish uchun sizga yana {spend_field.price - account.current_price} 💎 yetishmayapti!
                        """, show_alert=True
                    )
                else:
                    query.answer(
                        f"""
❌ Afsuski sizning promokod limitingiz bu oy uchun maksimalga yetdi.
Agarda ushbu taklifdan foydalanmoqchi bo'lsangiz admin bilan bog'laning.
                                                """, show_alert=True
                    )


def get_custom_promo(update: Update, context: CallbackContext):
    promo = update.message.text
    custom_promo_codes = CustomPromoCode.objects.filter(name=promo, status=True)
    if not custom_promo_codes.exists():
        update.message.reply_text(
            "❌ Kechirasiz, bu promo kod mavjud emas yoki ishlamayapti.",
        )
        return state.CHECK_PROMO

    first_promo = custom_promo_codes.first()
    custom_promo_code_account = CustomUserPromoCode.objects.filter(chat_id=update.effective_user.id,
                                                                   promo_code=first_promo)
    if custom_promo_code_account.exists():
        update.message.reply_text(
            "❌ Siz allaqachon ushbu promo kodni ishlatgansiz.",
            reply_markup=keyword.base()
        )
        return state.CHECK_PROMO
    if first_promo.count > 0:
        first_promo.count -= 1
        first_promo.save()

        user_account, _ = CustomUserAccount.objects.get_or_create(chat_id=update.effective_user.id)
        user_account.current_price += first_promo.reward
        user_account.total_price += first_promo.reward
        user_account.save()

        top_user, a = TopUser.objects.get_or_create(
            chat_id=update.effective_user.id,
            defaults={
                'fullname': update.effective_user.full_name,
            }
        )
        top_user.balance += first_promo.reward
        top_user.weekly_earned += first_promo.reward
        top_user.fullname = update.effective_user.full_name
        top_user.monthly_earned += first_promo.reward
        top_user.save()

        CustomUserPromoCode.objects.create(
            chat_id=update.effective_user.id,
            promo_code=first_promo,
        )

        update.message.reply_text(
            f"✅ Tabriklaymiz! Siz {first_promo.reward} 💎 bonus oldingiz.",
            reply_markup=keyword.base()
        )
        # try:
        #
        #     context.bot.send_message(chat_id=-1002144716834,
        #                              text=f"🎁 <code>{first_promo.count}/{first_promo.default}</code> <b>Promokod qoldi</b>",
        #                              parse_mode='HTML',
        #                              disable_web_page_preview=True)
        # except Exception:
        #     pass

    else:
        update.message.reply_text(
            "❌ Kechirasiz, bu promo kodning limitlari tugagan.",
            reply_markup=keyword.base()
        )

    return state.CHECK_PROMO
