from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from app.bot.states import States as state
from app.bot.messages.main import MessageText as msg_text
from app.models import Admin, TGUsers, Channel, Products
from django.db.models import Q
from app.bot.keyboards.base import Keyboards as kb, number as num


def admin(update: Update, context: CallbackContext):
    admin_id = update.effective_user.id
    admin_db = Admin.objects.filter(user_id=admin_id)
    if admin_db:
        update.message.reply_html(msg_text.is_admin.get('uz'), reply_markup=kb.admin('uz'))
        return state.admin


def bot_users(update: Update, context: CallbackContext):
    count = TGUsers.objects.all().count()
    last_50 = TGUsers.objects.all().order_by('-date_of_created')[:50]
    msg = f"Bot foydalanuvchilari soni: {count}\n\n"
    for user in last_50:
        msg += f"{user.id}) {user.fullname} | {user.date_of_created.strftime('%d.%m.%Y')}\n"
    update.message.reply_text(msg, reply_markup=kb.back('uz'))
    update.message.reply_html(msg_text.search_user.get('uz'), reply_markup=kb.back('uz'))
    return state.search_user


def search_user(update: Update, context: CallbackContext):
    users = TGUsers.objects.filter(fullname__icontains=update.message.text)
    if users:
        msg = f"Botdagi natijalari soni: {users.count()}\n\n"
        for user in users:
            msg += f"{user.id}) {user.fullname} | {user.date_of_created.strftime('%d.%m.%Y')}\n"
        update.message.reply_text(msg, reply_markup=kb.back('uz'))
    else:
        update.message.reply_html(msg_text.not_found_user.get('uz'), reply_markup=kb.back('uz'))
    return state.admin


def channel(update: Update, context: CallbackContext):
    channels = Channel.objects.all()
    msg_text = "Sizga tegishli kanallar ro'yxati:\n\n"
    for channel in channels:
        msg_text += f"{channel.id}) {channel.title} | {channel.url} | {channel.channel_id} | {channel.status}\n"
    update.message.reply_text(msg_text, reply_markup=kb.back('uz'))
    return state.channel_set


def channel_add(update: Update, context: CallbackContext):
    update.message.reply_html(msg_text.enter_channel_title.get('uz'), reply_markup=kb.back('uz'))
    return state.channel_add_title


def channel_add_title(update: Update, context: CallbackContext):
    title = update.message.text
    context.user_data['title'] = title
    update.message.reply_html(msg_text.enter_channel_url.get('uz'), reply_markup=kb.back('uz'))
    return state.channel_add_url


def channel_add_url(update: Update, context: CallbackContext):
    url = update.message.text
    context.user_data['url'] = url
    update.message.reply_html(msg_text.enter_channel_id.get('uz'), reply_markup=kb.back('uz'))
    return state.channel_add_id


def channel_add_id(update: Update, context: CallbackContext):
    channel_id = update.message.text
    context.user_data['channel_id'] = channel_id
    title = context.user_data['title']
    url = context.user_data['url']
    channel_id = context.user_data['channel_id']
    admin_id = update.effective_user.id
    admin_db = Admin.objects.get(user_id=admin_id)
    Channel.objects.create(title=title, url=url, channel_id=channel_id, owner_id=admin_db)
    update.message.reply_html(msg_text.succesfuly_added.get('uz'), reply_markup=kb.admin('uz'))
    return state.admin


def channel_one_set(update: Update, context: CallbackContext):
    channel_number = update.message.text
    if not channel_number.isdigit():
        update.message.reply_text('Siz raqam kiritmadingiz!!!')
        return state.channel_one_set
    try:
        channel = Channel.objects.get(id=channel_number)
    except Channel.DoesNotExist:
        update.message.reply_text('Bunday raqamli kanal mavjud emas!!!')
        return state.channel_set_one
    msg_txt = f"Kanal nomi: {channel.title}\nKanal havolasi: {channel.url}\nKanal ID: {channel.channel_id}\nKanal statusi: {channel.status} \n\n nimani o'zgartirmoqchisiz ?"
    context.user_data['channel_id'] = channel.id
    update.message.reply_text(msg_txt, reply_markup=kb.channel_one_set('uz'))
    return state.channel_set_one


def channel_one_set_status(update: Update, context: CallbackContext):
    channel = Channel.objects.get(id=context.user_data['channel_id'])
    if channel.status:
        channel.status = False
        channel.save()
        update.message.reply_text('Kanal o\'chirildi')
    else:
        channel.status = True
        channel.save()
        update.message.reply_text('Kanal yoqildi')
    return state.channel_set_one


def get_adm_stats(update: Update, context: CallbackContext):
    update.message.reply_text('Admin statistikasi')
    return state.admin


def admin_back(update: Update, context: CallbackContext):
    user = Admin.objects.filter(user_id=update.effective_user.id)
    if user:
        update.message.reply_html(msg_text.is_admin.get('uz'), reply_markup=kb.admin('uz'))
        return state.admin


def channel_del(update: Update, context: CallbackContext):
    channel_number = update.message.text
    if not channel_number.isdigit():
        update.message.reply_text('Siz raqam kiritmadingiz!!!')
        return state.channel_one_set
    try:
        channel = Channel.objects.get(id=channel_number)
    except Channel.DoesNotExist:
        update.message.reply_text('Bunday raqamli kanal mavjud emas!!!')
        return state.channel_set_one
    msg_txt = f"Kanal nomi: {channel.title}\nKanal havolasi: {channel.url}\nKanal ID: {channel.channel_id}\nKanal statusi: {channel.status} \n\n O'chiriladi"
    channel.delete()
    update.message.reply_text(msg_txt, reply_markup=kb.channel_deleted('uz'))
    return state.channel_set_one


def add_category(update: Update, context: CallbackContext):
    """Add category to project"""
    update.message.reply_text(msg_text.add_category.get('uz'))
    return state.add_category


def get_category(update: Update, context: CallbackContext):
    """Get category from user"""
    msg = update.message.text
    if '*' not in msg:
        update.message.reply_text('Siz xato kiritdingiz!!! \n\n Masalan: Lavash * Лаваш')
        return state.add_category
    uz, ru = msg.split('*')
    uz = uz.strip()
    ru = ru.strip()
    context.user_data['uz'] = uz
    context.user_data['ru'] = ru
    update.message.reply_text(msg_text.add_category_image_uz.get('uz'),
                              reply_markup=kb.back('uz'))
    return state.category_image_uz


def get_category_image_uz(update: Update, context: CallbackContext):
    """Get category image from user"""
    photo = update.message.photo[-1].file_id
    context.user_data['image_uz'] = photo
    update.message.reply_text(msg_text.add_category_image_ru.get('uz'),
                              reply_markup=kb.back('uz'))
    return state.category_image_ru