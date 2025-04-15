from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler, \
    CallbackQueryHandler
from django.conf import settings
from .methods.base import start, check_channel, add_to_channel, get_contact, get_contact_text
import logging
import time
from telegram.error import RetryAfter
from .states import States
from .messages.main import KeyboardText as msg_text

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
        ]
    },
    fallbacks=[CommandHandler('start', start),
               CommandHandler('admin', start),
               ]
)

dispatcher.add_handler(all_handler)
