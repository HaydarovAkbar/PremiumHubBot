from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts, Group, InvitedUser, CustomUserAccount, InvitedBonusUser
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()


def new_member_handler(update, context):
    message = update.message

    if message.new_chat_members:
        added_users = message.new_chat_members
        inviter = message.from_user

        for new_user in added_users:
            if new_user.id != inviter.id:
                invite_db, _ = InvitedUser.objects.get_or_create(
                    new_user_chat_id=new_user.id,
                    inviter_chat_id=inviter.id,
                )

                context.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


def get_group_base(update: Update, context: CallbackContext):
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
        query = update.callback_query
        if query.data == 'back':
            print("Back --------------->")
            query.delete_message()
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text="Menyuga qaytdik!",
                                     reply_markup=keyword.base())
            return state.START
        else:
            # query.delete_message()
            last_group = Group.objects.filter(is_active=True).last()
            if last_group:
                invited_count = InvitedUser.objects.filter(
                    inviter_chat_id=update.effective_user.id,
                ).count()
                if invited_count >= last_group.limit:
                    user_account, _ = CustomUserAccount.objects.get_or_create(
                        chat_id=update.effective_user.id,
                    )
                    invited_bonus_user = InvitedBonusUser.objects.get_or_create(
                        chat_id=update.effective_user.id,
                        group=last_group,
                    )
                    if invited_bonus_user.clean:
                        context.bot.send_message(chat_id=update.effective_user.id,
                                                 text="<b>Siz allaqachon bu guruhga odam qo'shib bonus olgansiz ❗️</b>",
                                                 parse_mode=ParseMode.HTML,
                                                 )
                    else:
                        user_account.current_price = user_account.current_price + last_group.price
                        user_account.total_price = user_account.total_price + last_group.price
                        user_account.save()
                        invited_bonus_user.clean = True
                        invited_bonus_user.save()
                        context.bot.send_message(chat_id=update.effective_user.id,
                                                 text="<b>🎉 Tabriklaymiz!</b>\n\n"
                                                      f"Siz guruhga yangi a'zolarni muvaffaqiyatli qo‘shdingiz va buning evaziga {last_group.price} so'mga ega bo‘ldingiz! 🔥\n\n"
                                                      "Doimiy ishtirok eting va yanada ko‘proq odamlarni qo‘shing — keyingi bonuslar sizni kutmoqda! 💰\n"
                                                      "Har bir faol harakatingiz uchun sizni mukofotlar bilan rag‘batlantiramiz! 🏆",
                                                 parse_mode="HTML"
                                                 )
                else:
                    context.bot.send_message(chat_id=update.effective_user.id,
                                             text=f"<b>Siz hali yetarlicha guruhga odam qo'shmadingiz ❗️</b>\n\nSiz yana {last_group.limit - invited_count} ta qo'shishingiz kerak!",
                                             parse_mode=ParseMode.HTML,
                                             )
            else:
                context.bot.send_message(chat_id=update.effective_user.id,
                                         text="<b>👇 Hozircha bonus uchun guruh kiritilmagan ❗️</b>",
                                         parse_mode=ParseMode.HTML,
                                         )
        return state.GROUP_BONUS
