from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler, \
    CallbackQueryHandler
from django.conf import settings

# from .methods.admin import admin
from .methods.base import start, check_channel, add_to_channel, get_contact, get_contact_text
from .methods.free_premium_and_stars import get_free_premium_and_stars, get_file_url
from .methods.prices import get_premium_prices, get_stars_prices
from .methods.rating import get_rating_base, get_rating_type
from .methods.bonus import get_bonus_base
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
        bot.set_webhook(webhook_url)
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
        CommandHandler('admin', start),
        MessageHandler(Filters.all, get_file_url),
    ],
    states={
        state.CHECK_CHANNEL: [
            CommandHandler('start', start),
            CommandHandler('admin', start),
            CallbackQueryHandler(add_to_channel),
        ],
        state.PHONE: [
            CommandHandler('start', start),
            CommandHandler('admin', start),
            MessageHandler(Filters.contact, get_contact),
            MessageHandler(Filters.text, get_contact_text),
        ],
        state.START: [
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][0] + ')$'), get_free_premium_and_stars),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][1] + ')$'), get_premium_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][2] + ')$'), get_stars_prices),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][3] + ')$'), get_rating_base),
            MessageHandler(Filters.regex('^(' + key_msg.base['uz'][4] + ')$'), get_bonus_base),
        ],
        state.RATING: [
            CommandHandler('start', start),
            CommandHandler('admin', start),
            CallbackQueryHandler(get_rating_type)
        ]
    },
    fallbacks=[CommandHandler('start', start),
               CommandHandler('admin', start),
               MessageHandler(Filters.all, get_file_url),
               ]
)

dispatcher.add_handler(all_handler)
