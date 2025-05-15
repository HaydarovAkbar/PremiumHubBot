from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from app.models import CustomUser, Channel, Prices, StarsPrices, TopUser
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()


def get_rating_base(update: Update, context: CallbackContext):
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
        # context.bot.send_message(chat_id=update.effective_user.id,
        #                          text="<b>Xush kelibsiz!</b> Real timeda statistika ko'rish imkoniyatiga ega bo'ling",
        #                          parse_mode=ParseMode.HTML,
        #                          reply_markup=keyword.delete
        #                          )
        _msg = """<b>🎉 Top Reytinglar</b>

Haftalik va oylik konkurslarda qatnashing <b>Telegram Premium va Telegram stars⭐️</b> yutib oling.🎁"""
        update.message.reply_html(
            _msg,
            reply_markup=keyword.rating(),
        )
        return state.RATING


# def get_rating_type(update: Update, context: CallbackContext):
#     all_channel = Channel.objects.filter(is_active=True)
#     left_channel = []
#     for channel in all_channel:
#         try:
#             a = context.bot.get_chat_member(chat_id=channel.chat_id, user_id=update.effective_user.id)
#             if a.status == 'left':
#                 left_channel.append(channel)
#         except Exception as e:
#             print(e)
#     if left_channel:
#         context.bot.send_message(chat_id=update.effective_user.id,
#                                  text="Botdan foydalanish uchun barcha kanallarga a'zo bo'ling)",
#                                  reply_markup=keyword.channels(left_channel))
#         return state.CHECK_CHANNEL
#     user_db = CustomUser.objects.get(chat_id=update.effective_user.id)
#     if user_db.is_active:
#         query = update.callback_query
#         query.answer()
#         if query.data == 'back':
#             query.delete_message()
#             context.bot.send_message(chat_id=update.effective_user.id,
#                                      text="Menyuga qaytdik!",
#                                      reply_markup=keyword.base())
#             return state.START
#         if query.data == 'top_rating':
#             _msg_ = "🏆TOP 20 ta foydalanuvchilar:\n\n"
#             top_20_user = TopUser.objects.order_by('-monthly_earned')[:20]
#             # top_20_user = CustomUser.objects.order_by('-current_price')[:20]
#             counter = 1
#             top_3 = {
#                 '1': '🥇',
#                 '2': '🥈',
#                 '3': '🥉'
#             }
#             for user in top_20_user:
#                 medal = top_3.get(str(counter), counter)
#                 _msg_ += f"{medal}. {user.fullname} - {user.monthly_earned} so'm\n"
#                 counter += 1
#             query.delete_message()
#             context.bot.send_message(chat_id=update.effective_user.id,
#                                      text=_msg_,
#                                      # reply_markup=keyword.back()
#                                      )
#         else:
#             _msg_ = "🏆TOP 10 ta haftalik foydalanuvchilar:\n\n"
#             top_20_user = TopUser.objects.order_by('-weekly_earned')[:10]
#             counter = 1
#             top_3 = {
#                 '1': '🥇',
#                 '2': '🥈',
#                 '3': '🥉'
#             }
#             for user in top_20_user:
#                 medal = top_3.get(str(counter), counter)
#                 _msg_ += f"{medal}. {user.fullname} - {user.monthly_earned} so'm\n"
#                 counter += 1
#             query.delete_message()
#             context.bot.send_message(chat_id=update.effective_user.id,
#                                      text=_msg_,
#                                      # reply_markup=keyword.back()
#                                      )
#
#     return state.RATING
