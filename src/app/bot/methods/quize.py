from django.conf import settings
from telegram import Update, InlineKeyboardMarkup, ParseMode, ReplyKeyboardRemove, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from app.models import CustomUser, CustomUserAccount, TopUser, Quiz, Question, UserAnswer

from .helpers_admin_quiz import build_question_grid, build_admin_preview_buttons

from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText
import re
from django.db import transaction
from telegram import Update
from telegram.ext import CallbackContext
from django.db.models import Max


keyword = Keyboards()
state = States()
msg = MessageText()
API_URL = f"https://api.telegram.org/bot{settings.TOKEN}/"


def add_quiz(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    try:
        custom_user = CustomUser.objects.get(chat_id=chat_id, is_admin=True)
    except CustomUser.DoesNotExist:
        return ConversationHandler.END

    update.message.reply_text("Iltimos, quiz nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    return state.QUIZ_TITLE


def quiz_title(update: Update, context: CallbackContext) -> int:
    title = update.message.text.strip()

    if not title:
        update.message.reply_text("Iltimos, quiz nomini bo'sh qoldirmang. Yana urinib ko'ring:")
        return state.QUIZ_TITLE

    new_quiz, _ = Quiz.objects.get_or_create(title=title)
    context.user_data['quiz_id'] = new_quiz.id
    example = """
savol matni 1
variant1|variant2|variant3|...

savol matni 2
a|b|c|d|e|f

savol matni 3

<code>#Eslatma:</code>
Har bir savol yangi qatorda bo'lishi kerak
To'g'ri javob har doim birinchi bo'lishi kerak
Javob variantlari | bilan ajratilishi kerak
...
    """
    update.message.reply_text("Endi savolni kiriting:")
    update.message.reply_text(example, parse_mode=ParseMode.HTML)
    return state.QUIZ_QUESTION


def quiz_question(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id

    # Faqat adminlarga ruxsat
    try:
        custom_user = CustomUser.objects.get(chat_id=chat_id, is_admin=True)
    except CustomUser.DoesNotExist:
        return ConversationHandler.END

    # Avval quiz_id bo'lishi shart
    quiz_id = context.user_data.get('quiz_id')
    if not quiz_id:
        update.message.reply_text("Iltimos, avval quiz nomini kiriting.")
        return ConversationHandler.END

    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        update.message.reply_text("Tanlangan quiz topilmadi.")
        return ConversationHandler.END

    raw_text = (update.message.text or "").strip()
    if not raw_text:
        update.message.reply_text("Iltimos, savollar matnini kiriting.")
        return state.QUIZ_QUESTION

    # Bloklarni bo'sh qatordan ajratamiz (2 yoki undan ko'p \n)
    blocks = [b.strip() for b in re.split(r'(?:\r?\n){2,}', raw_text) if b.strip()]

    if not blocks:
        update.message.reply_text("Bloklar topilmadi. Namuna:\n\nsavol matni 1\nvariant1|variant2|variant3\n\nsavol matni 2\na|b|c|d")
        return state.QUIZ_QUESTION

    # Keyingi orderni hisoblash
    max_order = quiz.questions.aggregate(m=Max('order'))['m'] or 0
    next_order = max_order + 1

    created = 0
    skipped = 0
    errors = []

    # Xavfsiz, atomic import
    with transaction.atomic():
        for bi, block in enumerate(blocks, start=1):
            # Har blok kamida 2 qator: 1-qator savol, 2-qator variantlar
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            if len(lines) < 2:
                skipped += 1
                errors.append(f"{bi}-blok: kamida 2 qator kerak (savol + variantlar).")
                continue

            question_text = lines[0]
            options_line = lines[1]

            # Variantlarni ajratish va tozalash
            options = [o.strip() for o in options_line.split("|") if o.strip()]
            if len(options) < 2:
                skipped += 1
                errors.append(f"{bi}-blok: kamida 2 ta variant bo'lishi kerak.")
                continue

            # Xohlasangiz limit qo'ying (ixtiyoriy):
            if len(options) > 6:
                skipped += 1
                errors.append(f"{bi}-blok: variantlar soni 10 tadan oshmasin.")
                continue

            # Question yaratamiz: to'g'ri javob kiritishda doim 1-variant
            Question.objects.create(
                quiz=quiz,
                text=question_text,
                options_text="|".join(options),
                order=next_order,
            )
            next_order += 1
            created += 1

    # Yakuniy javob
    msg = f"{created} ta savol muvaffaqiyatli qo'shildi."
    if skipped:
        msg += f"\n{skipped} ta blok o'tkazib yuborildi."
    if errors:
        # 3-4 ta xatoni ko'rsatish kifoya, qolganini qisqartiramiz
        preview = "\n".join(errors[:5])
        if len(errors) > 5:
            preview += f"\n... yana {len(errors)-5} ta xatolik"
        msg += f"\n\nXatolar:\n{preview}"

    update.message.reply_text(msg)
    update.message.reply_text("Yana savol qo'shasizmi? (ha/yo'q)")

    return state.QUIZ_ADD_MORE


def quiz_add_more(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    try:
        custom_user = CustomUser.objects.get(chat_id=chat_id, is_admin=True)
    except CustomUser.DoesNotExist:
        return ConversationHandler.END

    response = update.message.text.strip().lower()
    if response in ['ha', 'yes', 'y']:
        update.message.reply_text("Iltimos, savolni kiriting:")
        return state.QUIZ_QUESTION
    elif response in ['yo\'q', 'no', 'n']:
        update.message.reply_text("Quiz yaratish tugallandi. Rahmat!", reply_markup=keyword.admin_base())
        return ConversationHandler.END
    else:
        update.message.reply_text("Iltimos, faqat 'ha' yoki 'yo'q' deb javob bering.")
        return state.QUIZ_ADD_MORE


# def delete_quiz(update: Update, context: CallbackContext) -> int:
#     chat_id = update.effective_chat.id
#     try:
#         custom_user = CustomUser.objects.get(chat_id=chat_id, is_admin=True)
#     except CustomUser.DoesNotExist:
#         return ConversationHandler.END
#
#     quizzes = Quiz.objects.all()
#     if not quizzes.exists():
#         update.message.reply_text("Hozircha hech qanday quiz mavjud emas.", reply_markup=keyword.admin_base())
#         return ConversationHandler.END
#
#     buttons = [[InlineKeyboardButton(q.title, callback_data=f"delete_{q.id}")] for q in quizzes]
#     reply_markup = InlineKeyboardMarkup(buttons)
#
#     update.message.reply_text("Iltimos, o'chirmoqchi bo'lgan quizni tanlang:", reply_markup=reply_markup)
#     return state.QUIZ_DELETE_SELECT
#
#
# def quiz_delete_select(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     data = query.data
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=f"Quiz o'chirilmoqda, iltimos kuting... {data}"
#     )
#     if not data.startswith("delete_"):
#         query.edit_message_text("Noto'g'ri tanlov. Iltimos, qayta urinib ko'ring.", reply_markup=keyword.admin_base())
#         return ConversationHandler.END
#
#     quiz_id = int(data.split("_")[1])
#     try:
#         quiz = Quiz.objects.get(id=quiz_id)
#         Question.objects.filter(quiz=quiz).delete()
#         quiz.delete()
#         query.edit_message_text(f"Quiz '{quiz.title}' muvaffaqiyatli o'chirildi.", reply_markup=keyword.admin_base())
#     except Quiz.DoesNotExist:
#         query.edit_message_text("Tanlangan quiz topilmadi. Iltimos, qayta urinib ko'ring.", reply_markup=keyword.admin_base())
#
#     return ConversationHandler.END


# 1) Quizzarni tanlash
def delete_quiz(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    try:
        CustomUser.objects.get(chat_id=chat_id, is_admin=True)
    except CustomUser.DoesNotExist:
        return ConversationHandler.END

    quizzes = Quiz.objects.order_by('-created_at')
    if not quizzes.exists():
        update.message.reply_text("Hozircha hech qanday quiz mavjud emas.", reply_markup=keyword.admin_base())
        return ConversationHandler.END

    # prefiks: quizsel:<id>
    buttons, row = [], []
    for q in quizzes:
        row.append(InlineKeyboardButton(q.title[:64], callback_data=f"quizsel:{q.id}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("↩️ Bekor", callback_data="quiz:cancel")])

    update.message.reply_text(
        "Iltimos, boshqarish uchun quizzarni tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return state.QUIZ_DELETE_SELECT  # yoki alohida state; callbacklar bilan davom etamiz

# 2) Tanlangan quizz uchun boshqaruv panel + savollar grid
def quiz_admin_panel(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = (query.data or "").strip()

    # qayerdan keldi: quizsel:<id> yoki quizpanel:<id>
    m = re.match(r"^(?:quizsel|quizpanel):(\d+)$", data)
    if not m:
        query.edit_message_text("Noto‘g‘ri tanlov.", reply_markup=keyword.admin_base())
        return ConversationHandler.END

    quiz_id = int(m.group(1))
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        query.edit_message_text("Quiz topilmadi.", reply_markup=keyword.admin_base())
        return ConversationHandler.END

    qcount = quiz.questions.count()
    text = f"🧩 <b>{quiz.title}</b>\n\nSavollar soni: <b>{qcount}</b>"
    query.edit_message_text(
        text=text,
        reply_markup=build_question_grid(quiz),
        parse_mode="HTML"
    )
    return state.QUIZ_DELETE_SELECT

# 3) Bitta savolni admin-preview (shuffle + ✅ bilan)
def quiz_preview_question(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = (query.data or "").strip()

    m = re.match(r"^qprev:(\d+)$", data)
    if not m:
        query.answer("Noto‘g‘ri tanlov")
        return ConversationHandler.END

    qid = int(m.group(1))
    try:
        question = Question.objects.select_related('quiz').get(id=qid)
    except Question.DoesNotExist:
        query.edit_message_text("Savol topilmadi.", reply_markup=keyword.admin_base())
        return ConversationHandler.END

    # Admin preview: foydalanuvchiga ko‘ringanidek, lekin to‘g‘ri javobga ✅
    query.edit_message_text(
        text=question.text,
        reply_markup=build_admin_preview_buttons(question)
    )
    return state.QUIZ_DELETE_SELECT

# 4) Butun quizzni o‘chirish – tasdiqlash
def quiz_delete_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = (query.data or "").strip()

    m = re.match(r"^quizdel:(\d+)$", data)
    if not m:
        query.answer("Noto‘g‘ri tanlov")
        return ConversationHandler.END

    quiz_id = int(m.group(1))
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        query.edit_message_text("Quiz topilmadi.", reply_markup=keyword.admin_base())
        return ConversationHandler.END

    qcount = quiz.questions.count()
    text = f"⚠️ <b>{quiz.title}</b> ni va unga tegishli <b>{qcount}</b> ta savolni o‘chirmoqchisiz.\n\nTasdiqlaysizmi?"
    buttons = [
        [
            InlineKeyboardButton("✅ Ha, o‘chir", callback_data=f"quizdelrun:{quiz.id}"),
            InlineKeyboardButton("↩️ Yo‘q, orqaga", callback_data=f"quizpanel:{quiz.id}"),
        ]
    ]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
    return state.QUIZ_DELETE_SELECT

def quiz_delete_run(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = (query.data or "").strip()
    m = re.match(r"^quizdelrun:(\d+)$", data)
    if not m:
        query.answer("Noto‘g‘ri tanlov")
        return ConversationHandler.END

    quiz_id = int(m.group(1))
    try:
        with transaction.atomic():
            quiz = Quiz.objects.select_for_update().get(id=quiz_id)
            title = quiz.title
            cnt = quiz.questions.count()
            quiz.questions.all().delete()
            quiz.delete()
        query.edit_message_text(f"✅ Quiz '{title}' va {cnt} ta savol o‘chirildi.", reply_markup=keyword.admin_base())
    except Quiz.DoesNotExist:
        query.edit_message_text("Quiz topilmadi.", reply_markup=keyword.admin_base())
    return ConversationHandler.END

# 5) Bitta savolni o‘chirish – tasdiqlash va bajarish
def question_delete_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = (query.data or "").strip()

    m = re.match(r"^qdel:(\d+)$", data)
    if not m:
        query.answer("Noto‘g‘ri tanlov")
        return ConversationHandler.END

    qid = int(m.group(1))
    try:
        question = Question.objects.select_related('quiz').get(id=qid)
    except Question.DoesNotExist:
        query.edit_message_text("Savol topilmadi.", reply_markup=keyword.admin_base())
        return ConversationHandler.END

    buttons = [
        [
            InlineKeyboardButton("✅ Ha, o‘chir", callback_data=f"qdelrun:{qid}"),
            InlineKeyboardButton("↩️ Yo‘q, orqaga", callback_data=f"quizpanel:{question.quiz_id}"),
        ]
    ]
    query.edit_message_text(
        f"⚠️ '{question.text[:70]}...' savolini o‘chirmoqchimisiz?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return state.QUIZ_DELETE_SELECT

def question_delete_run(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = (query.data or "").strip()
    m = re.match(r"^qdelrun:(\d+)$", data)
    if not m:
        query.answer("Noto‘g‘ri tanlov")
        return ConversationHandler.END

    qid = int(m.group(1))
    try:
        with transaction.atomic():
            q = Question.objects.select_related('quiz').select_for_update().get(id=qid)
            quiz_id = q.quiz_id
            q.delete()
        # o‘chirgandan keyin quiz panelga qaytamiz
        quiz = Quiz.objects.get(id=quiz_id)
        query.edit_message_text(
            "✅ Savol o‘chirildi. Quyida yangilangan ro‘yxat:",
            reply_markup=build_question_grid(quiz)
        )
    except Question.DoesNotExist:
        query.edit_message_text("Savol topilmadi.", reply_markup=keyword.admin_base())
    except Quiz.DoesNotExist:
        query.edit_message_text("Quiz topilmadi.", reply_markup=keyword.admin_base())
    return state.QUIZ_DELETE_SELECT


def universal_quiz_callback_data(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    data = (query.data or "").strip()

    # Admin quiz boshqaruvi
    if data.startswith("quizsel:") or data.startswith("quizpanel:"):
        return quiz_admin_panel(update, context)
    if data.startswith("qprev:"):
        return quiz_preview_question(update, context)
    if data.startswith("quizdel:"):
        return quiz_delete_confirm(update, context)
    if data.startswith("quizdelrun:"):
        return quiz_delete_run(update, context)
    if data.startswith("qdel:"):
        return question_delete_confirm(update, context)
    if data.startswith("qdelrun:"):
        return question_delete_run(update, context)
    if data == "quiz:cancel" or data == "noop":
        query.answer("OK")
        try:
            query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        return ConversationHandler.END