# helpers_admin_quiz.py
import math
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# Savollar raqamlarini grid ko‘rinishda (max cols = 8) chiqarish
def build_question_grid(quiz, cols=8):
    qs = list(quiz.questions.order_by('order', 'id').values_list('id', flat=True))
    n = len(qs)
    buttons, row = [], []
    for i, qid in enumerate(qs, start=1):
        row.append(InlineKeyboardButton(str(i), callback_data=f"qprev:{qid}"))
        if len(row) == cols:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    # pastki boshqaruvlar
    buttons.append([
        InlineKeyboardButton("🗑️ Butun quizni o‘chirish", callback_data=f"quizdel:{quiz.id}"),
        InlineKeyboardButton("↩️ Bekor", callback_data="quiz:cancel"),
    ])
    return InlineKeyboardMarkup(buttons)


# Admin preview uchun savol tugmalari (shuffle + to‘g‘ri javobga ✅)
def build_admin_preview_buttons(question):
    # options() -> ["javob1","javob2",...]
    opts = list(enumerate(question.options(), start=1))  # [(1,"j1"),(2,"j2"),...]
    random.shuffle(opts)  # foydalanuvchiga ko‘ringan tartib

    buttons, row = [], []
    for orig_idx, label in opts:
        is_correct = (orig_idx == 1)  # kiritishda 1-variant to‘g‘ri
        title = f"{'✅ ' if is_correct else ''}{label}"
        # admin preview – noop callback (bosilganda hech narsa qilmaydi)
        row.append(InlineKeyboardButton(title, callback_data="noop"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # pastki boshqaruvlar
    buttons.append([
        InlineKeyboardButton("🗑️ Bu savolni o‘chirish", callback_data=f"qdel:{question.id}"),
        InlineKeyboardButton("⬅️ Savollar ro‘yxati", callback_data=f"quizpanel:{question.quiz_id}"),
    ])
    return InlineKeyboardMarkup(buttons)
