from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler, \
    CallbackQueryHandler
from django.conf import settings

# from .methods.admin import admin
from .methods.base import start, check_channel, add_to_channel, get_contact, get_contact_text, manual, adminstrator
from .methods.free_premium_and_stars import get_free_premium_and_stars, get_file_url
from .methods.prices import get_premium_prices, get_stars_prices
from .methods.rating import get_rating_base #, get_rating_type
from .methods.bonus import get_bonus_base   # get_bonus_type, get_daily_bonus, get_stories_bonus
from .methods.group import new_member_handler #get_group_base
# from .methods.interesting_bonus import get_interesting_bonus_base , check_interesting_bonus_nik, \
#     check_interesting_bonus_bio
from .methods.account import my_account, universal_callback_data # spend, spend_field, get_promo_code, send_promo_code
from .methods.admin import admin_base, ads, get_ads, parse_button, received_advert, get_kill_id, kill_task, get_user_id, \
    get_user, confirm_kill_task, info_promo, get_all_promo_codes, passive, get_balance, push_balance, send_msg, \
    user_profile, get_all_stories
import logging
import time
from telegram.error import RetryAfter
from .states import States
from .messages.main import KeyboardText

key_msg = KeyboardText()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.WARNING)

logger = logging.getLogger(__name__)


def run():
    # bot.set_webhook(settings.HOST + '/api/schema/')
    webhook_url = settings.HOST + '/premium/'
    print('started webhook')
    try:
        bot.set_webhook(webhook_url, allowed_updates=["message", "callback_query", "chat_boost", "removed_chat_boost"])
    except RetryAfter as e:
        time.sleep(e.retry_after)
        bot.set_webhook(webhook_url)


TOKEN = settings.TOKEN

bot: Bot = Bot(token=TOKEN)
state = States()

dispatcher = Dispatcher(bot, None)

all_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        CommandHandler('admin', admin_base),
        CommandHandler('promo', info_promo),
        CommandHandler('promocodes', get_all_promo_codes),
        CommandHandler('stories', get_all_stories),
        MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
        MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
        MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
        MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
        MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
        MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
        MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
        MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),

        # MessageHandler(Filters.all, get_file_url),
    ],
    states={
        state.CHECK_CHANNEL: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(add_to_channel),
        ],
        state.PHONE: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.contact, get_contact),
            # MessageHandler(Filters.text, get_contact_text),
        ],
        state.START: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
            CallbackQueryHandler(universal_callback_data)
        ],
        state.RATING: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
            MessageHandler(Filters.regex('^(' + key_msg.back['uz'] + ')$'), start),
        ],
        state.BONUS: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.CHANNEL_BOOST_BONUS: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base), CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.STORY_BONUS: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.GROUP_BONUS: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.INTERESTING_BONUS: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.INTERESTING_BONUS_NIK: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.INTERESTING_BONUS_BIO: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.MY_ACCOUNT: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.GET_PROMO_CODE: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.SEND_PROMO_CODE: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            CallbackQueryHandler(universal_callback_data),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
        ],
        state.ADMIN: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + key_msg.back['uz'] + ')$'), admin_base),
            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
        ],
        state.CONFIRM: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            MessageHandler(Filters.regex('^(' + key_msg.back['uz'] + ')$'), admin_base),
            MessageHandler(Filters.regex('^(' + "✅ Tasdiqlash" + ')$'), confirm_kill_task),
        ],
        state.USER_ID: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            MessageHandler(Filters.regex('^(' + key_msg.back['uz'] + ')$'), admin_base),
            MessageHandler(Filters.text, get_user),
        ],
        state.ADS: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            MessageHandler(Filters.regex('^(' + key_msg.back['uz'] + ')$'), admin_base),
            MessageHandler(Filters.regex('^(' + "📳 Davom etish" + ')$'), get_ads),
            MessageHandler(Filters.text, parse_button),
        ],
        state.ADS_BUTTON: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            MessageHandler(Filters.regex('^(' + key_msg.back['uz'] + ')$'), admin_base),
            # MessageHandler(Filters.regex('^(' + "📳 Davom etish" + ')$'), received_advert),
            MessageHandler(Filters.all, received_advert),
        ],
        state.KILL_TASK: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            MessageHandler(Filters.regex('^(' + key_msg.back['uz'] + ')$'), admin_base),
            MessageHandler(Filters.text, get_kill_id),
        ],
        state.PASSIVE: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            CallbackQueryHandler(passive),
        ],
        state.USER_PROFILE: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            CallbackQueryHandler(user_profile),
        ],
        state.GET_BALANCE: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            MessageHandler(Filters.text, get_balance)
        ],
        state.PUSH_BALANCE: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            MessageHandler(Filters.text, push_balance)
        ],
        state.SEND_MSG: [
            CommandHandler('start', start),
            CommandHandler('admin', admin_base),
            CommandHandler('promo', info_promo),
            CommandHandler('promocodes', get_all_promo_codes),
            CommandHandler('stories', get_all_stories),

            MessageHandler(Filters.regex('^(' + "💠 Xabar yuborish" + ')$'), ads),
            MessageHandler(Filters.regex('^(' + "🛑 Xabarni to'xtatish" + ')$'), kill_task),
            MessageHandler(Filters.regex('^(' + "🔍 Foydalanuvchi qidirish" + ')$'), get_user_id),
            MessageHandler(Filters.text, send_msg)
        ]
    },
    fallbacks=[CommandHandler('start', start),
               CommandHandler('admin', admin_base),
               CommandHandler('promo', info_promo),
               CommandHandler('promocodes', get_all_promo_codes),
               CommandHandler('stories', get_all_stories),

               MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
               MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
               MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
               MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
               MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
               MessageHandler(Filters.regex('^(' + key_msg.base['uz'][5] + ')$'), my_account),
               MessageHandler(Filters.regex('^(' + key_msg.base['uz'][6] + ')$'), manual),
               MessageHandler(Filters.regex('^(' + key_msg.base['uz'][7] + ')$'), adminstrator),
               # MessageHandler(Filters.all, get_file_url),
               ]
)
# new_member_handler = MessageHandler(Filters.status_update.new_chat_members, new_member_handler)
# dispatcher.add_handler(new_member_handler)
dispatcher.add_handler(all_handler)
