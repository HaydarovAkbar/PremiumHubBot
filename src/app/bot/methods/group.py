from app.models import CustomUser, Channel, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, \
    StoryBonusAccounts, Group, InvitedUser, CustomUserAccount, InvitedBonusUser, TopUser
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
        # print(inviter)
        last_group = Group.objects.filter(is_active=True).last()

        for new_user in added_users:
            if new_user.id != inviter.id:
                invite_db, _ = InvitedUser.objects.get_or_create(
                    new_user_chat_id=new_user.id,
                    inviter_chat_id=inviter.id,
                    group_id=last_group.id,
                )
                if _:
                    new_user_fullname = inviter.first_name + " " + inviter.last_name
                    new_user_id = inviter.id
                    minio = f"<a href='tg://user?id={new_user_id}'>{new_user_fullname}</a>"
                    context.bot.send_message(chat_id=inviter.id,
                                             text=f"""Siz {minio} ni guruhga qo'shganingiz uchun sizga bonus beriladi\n'♻️ Tekshirish' tugmasi orqali bonusingizni oling""")
                context.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)