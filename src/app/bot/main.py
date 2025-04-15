from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler, \
    CallbackQueryHandler
from django.conf import settings
from .methods.base import start
import logging
from .states import States as state
from .messages.main import KeyboardText as msg_text

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.WARNING)

logger = logging.getLogger(__name__)


def run():
    print('started webhook')
    bot.set_webhook(settings.HOST + '/bot/')


TOKEN = settings.TOKEN

bot: Bot = Bot(token=TOKEN)

dispatcher = Dispatcher(bot, None)

all_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
    ],
    states={
    },
    fallbacks=[CommandHandler('start', start), ]
)

dispatcher.add_handler(all_handler)
