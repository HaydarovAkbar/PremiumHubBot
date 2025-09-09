# # bot/handlers_test_bonus.py
# from __future__ import annotations
# import random
# from decimal import Decimal
#
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     CallbackContext,
#     ConversationHandler,
#     CommandHandler,
#     CallbackQueryHandler,
# )
#
# from app.models import Question, CustomUser
# from .services_test import (
#     can_start_test,
#     register_attempt_start,
#     pick_random_question_ids,
#     compute_bonus,
#     flush_results_to_db,
#     get_settings,
# )
# from ..keyboards.base import Keyboards
# from ..states import States
# from ..messages.main import MessageText
# import re
# from django.db import transaction
# from telegram import Update
# from telegram.ext import CallbackContext
# from django.db.models import Max
#
#
# keyword = Keyboards()
# state = States()
# msg = MessageText()
#
# # TEST_BONUS = state.TEST_BONUS
#
#
# # Entry nuqta: tugma yoki /test_bonus
# def entry_test_bonus(update: Update, context: CallbackContext) -> int:
#     # foydalanuvchini topamiz
#     user = CustomUser.objects.filter(chat_id=update.effective_user.id, is_blocked=False).first()
#     if not user:
#         (update.message or update.callback_query).reply_text("Avval ro‘yxatdan o‘ting.")
#         return ConversationHandler.END
#
#     ok, settings_or_msg = can_start_test(user)
#     if not ok:
#         msg = settings_or_msg  # xatolik matni
#         (update.message or update.callback_query).reply_text(f"❌ {msg}")
#         return ConversationHandler.END
#
#     s = settings_or_msg  # GlobalTestSettings
#
#     qids = pick_random_question_ids(s.question_limit, only_active=True)
#     if not qids:
#         (update.message or update.callback_query).reply_text("Hozircha aktiv savollar topilmadi.")
#         return ConversationHandler.END
#
#     # urinishni 1 marta DBda ro‘yxatga olamiz (daily/total limitlar uchun)
#     register_attempt_start(user)
#
#     # Sessiya konteksti (RAM)
#     context.user_data["tb"] = {
#         "qids": qids,
#         "i": 0,
#         "correct": 0,
#         "per": s.per_correct_bonus,
#         "full": s.full_completion_bonus,
#         "shuffle": s.shuffle_options,
#     }
#
#     txt = (
#         "💎 Test boshlandi!\n"
#         f"- Savollar: {len(qids)} ta\n"
#         f"- Har to‘g‘ri javob: {s.per_correct_bonus}\n"
#         f"- Hammasi to‘g‘ri bo‘lsa: {s.full_completion_bonus}\n\n"
#         "Boshlaymiz!"
#     )
#     if update.message:
#         update.message.reply_text(txt)
#     else:
#         update.callback_query.edit_message_text(txt)
#
#     return _send_next(update, context)
#
#
# def _send_next(update: Update, context: CallbackContext) -> int:
#     data = context.user_data.get("tb")
#     if not data:
#         (update.callback_query or update.message).reply_text("Sessiya topilmadi.")
#         return ConversationHandler.END
#
#     i = data["i"]
#     qids = data["qids"]
#
#     if i >= len(qids):
#         return _finish(update, context)
#
#     qid = qids[i]
#     q = Question.objects.get(id=qid)
#
#     opts = list(enumerate(q.options(), start=1))  # [(1,"javob1"), (2,"javob2"), ...]
#     if data.get("shuffle", True):
#         random.shuffle(opts)
#
#     # 2 ustunli inline klaviatura
#     buttons, row = [], []
#     for orig_idx, label in opts:
#         row.append(InlineKeyboardButton(label, callback_data=f"tb:{qid}:{orig_idx}"))
#         if len(row) == 2:
#             buttons.append(row)
#             row = []
#     if row:
#         buttons.append(row)
#
#     kb = InlineKeyboardMarkup(buttons)
#
#     if update.callback_query:
#         update.callback_query.edit_message_text(q.text, reply_markup=kb)
#     else:
#         update.message.reply_text(q.text, reply_markup=kb)
#
#     return state.TEST_BONUS
#
#
# def on_answer(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#
#     data = context.user_data.get("tb")
#     if not data:
#         query.edit_message_text("Sessiya yo‘q. /start dan qayta urinib ko‘ring.")
#         return ConversationHandler.END
#
#     parts = (query.data or "").split(":")
#     if len(parts) != 3 or parts[0] != "tb":
#         query.answer("Noto‘g‘ri javob.")
#         return state.TEST_BONUS
#
#     # asl indeks bo‘yicha tekshiruv (kiritishda 1-variant to‘g‘ri)
#     orig_idx = int(parts[2])
#     if orig_idx == 1:
#         data["correct"] += 1
#
#     data["i"] += 1
#     context.user_data["tb"] = data
#
#     # idempotentlik: eski klaviaturani tozalab qo‘yamiz
#     try:
#         query.edit_message_reply_markup(reply_markup=None)
#     except Exception:
#         pass
#
#     return _send_next(update, context)
#
#
# def _finish(update: Update, context: CallbackContext) -> int:
#     # Foydalanuvchi
#     user = CustomUser.objects.filter(chat_id=update.effective_user.id).first()
#     data = context.user_data.get("tb") or {}
#
#     correct = int(data.get("correct", 0))
#     total = len(data.get("qids", []))
#     per = data.get("per", Decimal("0.00"))
#     full = data.get("full", Decimal("0.00"))
#
#     earned = compute_bonus(correct, total, per, full)
#     flush_results_to_db(user, correct, total, earned)
#
#     result_text = (
#         "✅ Test yakunlandi!\n"
#         f"To‘g‘ri: {correct}/{total}\n"
#         f"Har to‘g‘ri: {per}\n"
#         f"To‘liq to‘g‘ri bonusi: {full}\n"
#         f"Jami bonus: {earned}"
#     )
#     if update.callback_query:
#         update.callback_query.edit_message_text(result_text)
#     else:
#         update.message.reply_text(result_text)
#
#     context.user_data.pop("tb", None)
#     return ConversationHandler.END
# #
# #
# # # ConversationHandler registratsiyasi (skelet)
# # def register_test_bonus_handlers(dispatcher):
# #     conv = ConversationHandler(
# #         entry_points=[
# #             CommandHandler("test_bonus", entry_test_bonus),
# #             CallbackQueryHandler(entry_test_bonus, pattern=r"^start_test_bonus$"),
# #         ],
# #         states={
# #             state.TEST_BONUS: [
# #                 CallbackQueryHandler(on_answer, pattern=r"^tb:\d+:\d+$"),
# #             ],
# #         },
# #         fallbacks=[],
# #         allow_reentry=True,
# #     )
# #     dispatcher.add_handler(conv)

# bot/handlers_test_bonus.py
from __future__ import annotations

import random
from decimal import Decimal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
)

from django.db.models import F

# MODELLAR
from app.models import Question, CustomUser

# XIZMATLAR
from .services_test import (
    can_start_test,
    register_attempt_start,
    pick_random_question_ids,
    compute_bonus,
    flush_results_to_db,
    get_settings,
    get_starting_balance,   # services_test.py da bor
)

# UI
from ..keyboards.base import Keyboards
from ..states import States
from ..messages.main import MessageText

keyword = Keyboards()
state = States()
msg = MessageText()


# -------------------------
# YORDAMCHI FUNKSIYALAR
# -------------------------

def _progress_header(data: dict) -> str:
    """Har savolda yuqoriga qisqa statistikani chiqarish."""
    step = data["i"] + 1                             # 1-based
    total = len(data["qids"])
    correct = data["correct"]
    per = data["per"]
    start_balance = data.get("start_balance", Decimal("0.00"))

    earned_so_far = per * Decimal(correct)
    header = (
        f"💎 Test ({step}/{total})\n"
        f"— To‘g‘ri: {correct}\n"
        f"— Topilgan: {earned_so_far}\n"
        f"— Balansingiz: {start_balance + earned_so_far}"
    )
    return header


def _send_next(update: Update, context: CallbackContext) -> int:
    """Navbatdagi savolni yuborish yoki testni yakunlash."""
    data = context.user_data.get("tb")
    if not data:
        (getattr(update, "callback_query", None) or update.message).reply_text("Sessiya topilmadi.")
        return ConversationHandler.END

    i = data["i"]
    qids = data["qids"]

    if i >= len(qids):
        return _finish(update, context)

    q = Question.objects.get(id=qids[i])

    # Variantlar: asl indeks (1 doim to‘g‘ri) saqlanadi
    opts = list(enumerate(q.options(), start=1))
    if data.get("shuffle", True):
        random.shuffle(opts)

    # 2 ustunli klaviatura + “🏁 Yakunlash”
    buttons, row = [], []
    for orig_idx, label in opts:
        row.append(InlineKeyboardButton(label, callback_data=f"tb:{q.id}:{orig_idx}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🏁 Yakunlash va balansga o'tkazish", callback_data="tb_finish")])

    kb = InlineKeyboardMarkup(buttons)

    # Matn: progress + savol
    header = _progress_header(data)
    text = f"{header}\n\n{q.text}"

    if update.callback_query:
        update.callback_query.edit_message_text(text, reply_markup=kb)
    else:
        update.message.reply_text(text, reply_markup=kb)

    return state.TEST_BONUS


# -------------------------
# ENTRY
# -------------------------

def entry_test_bonus(update: Update, context: CallbackContext) -> int:
    """Tugma yoki /test_bonus orqali kirish."""
    user = CustomUser.objects.filter(chat_id=update.effective_user.id, is_blocked=False).first()
    if not user:
        (update.message or update.callback_query).reply_text("Avval ro‘yxatdan o‘ting.")
        return ConversationHandler.END

    ok, settings_or_msg = can_start_test(user)
    if not ok:
        (update.message or update.callback_query).reply_text(f"❌ {settings_or_msg}")
        return ConversationHandler.END
    s = settings_or_msg  # GlobalTestSettings

    qids = pick_random_question_ids(s.question_limit, only_active=True)
    if not qids:
        (update.message or update.callback_query).reply_text("Hozircha aktiv savollar topilmadi.")
        return ConversationHandler.END

    # Limit hisoblari uchun faqat boshlaganda DBga yozamiz
    register_attempt_start(user)

    # Real-time balansni ko‘rsatish uchun start balans
    start_balance = get_starting_balance(user)

    # Sessiya (RAM)
    context.user_data["tb"] = {
        "qids": qids,
        "i": 0,
        "correct": 0,
        "per": s.per_correct_bonus,
        "full": s.full_completion_bonus,
        "shuffle": s.shuffle_options,
        "start_balance": start_balance,
    }

    intro = (
        "💎 Test boshlandi!\n"
        f"- Savollar: {len(qids)} ta\n"
        f"- Har to‘g‘ri javob: {s.per_correct_bonus}\n"
        f"- Hammasi to‘g‘ri bo‘lsa: {s.full_completion_bonus}\n\n"
        "Boshlaymiz!"
    )
    if update.message:
        update.message.reply_text(intro)
    else:
        update.callback_query.edit_message_text(intro)

    return _send_next(update, context)


# -------------------------
# ANSWER / FINISH HANDLERS
# -------------------------

def on_answer(update: Update, context: CallbackContext) -> int:
    """Foydalanuvchi variantni bosganda."""
    query = update.callback_query
    query.answer()

    data = context.user_data.get("tb")
    if not data:
        query.edit_message_text("Sessiya yo‘q. /start dan qayta urinib ko‘ring.")
        return ConversationHandler.END

    parts = (query.data or "").split(":")
    if len(parts) != 3 or parts[0] != "tb":
        query.answer("Noto‘g‘ri javob.")
        return state.TEST_BONUS

    # Asl indeks bo‘yicha tekshiruv (1-variant to‘g‘ri)
    orig_idx = int(parts[2])
    if orig_idx == 1:
        data["correct"] += 1

    data["i"] += 1
    context.user_data["tb"] = data

    # Xabarni to‘liq yangilab navbatdagisini yuboramiz
    return _send_next(update, context)


def on_finish_now(update: Update, context: CallbackContext) -> int:
    """Foydalanuvchi istalgan payt '🏁 Yakunlash'ni bossin."""
    return _finish(update, context)


def _finish(update: Update, context: CallbackContext) -> int:
    """Yakunda bonus va statistika yoziladi."""
    user = CustomUser.objects.filter(chat_id=update.effective_user.id).first()
    data = context.user_data.get("tb") or {}

    correct = int(data.get("correct", 0))
    total = len(data.get("qids", []))
    per = data.get("per", Decimal("0.00"))
    full = data.get("full", Decimal("0.00"))
    start_balance = data.get("start_balance", Decimal("0.00"))

    earned = compute_bonus(correct, total, per, full)
    flush_results_to_db(user, correct, total, earned)

    result_text = (
        "✅ Test yakunlandi!\n"
        f"To‘g‘ri: {correct}/{total}\n"
        f"Har to‘g‘ri: {per}\n"
        f"To‘liq to‘g‘ri bonusi: {full}\n"
        f"Jami bonus: {earned}\n"
        f"Yangi balans: {start_balance + earned}"
    )
    if update.callback_query:
        update.callback_query.edit_message_text(result_text)
    else:
        update.message.reply_text(result_text)

    context.user_data.pop("tb", None)
    return ConversationHandler.END


# # -------------------------
# # REGISTRATSIYA
# # -------------------------
#
# def register_test_bonus_handlers(dispatcher):
#     conv = ConversationHandler(
#         entry_points=[
#             CommandHandler("test_bonus", entry_test_bonus),
#             CallbackQueryHandler(entry_test_bonus, pattern=r"^start_test_bonus$"),
#         ],
#         states={
#             state.TEST_BONUS: [
#                 CallbackQueryHandler(on_answer, pattern=r"^tb:\d+:\d+$"),
#                 CallbackQueryHandler(on_finish_now, pattern=r"^tb_finish$"),
#             ],
#         },
#         fallbacks=[],
#         allow_reentry=True,
#     )
#     dispatcher.add_handler(conv)
