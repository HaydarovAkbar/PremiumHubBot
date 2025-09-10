# bot/handlers_test_bonus.py
from __future__ import annotations

import random
from decimal import Decimal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ParseMode
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
    # flush_results_to_db,
    flush_partial_to_db,
    get_settings,
    get_starting_balance,  # services_test.py da bor
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

def motivational_text(correct: int, total: int) -> str:
    # total katta/oz bo'lishi mumkin; cheklovlarni foiz bo'yicha ham qilsa bo'ladi.
    # Hozir siz bergan diapazon (20 ta savol) ruhida:
    msgs = []
    if correct <= 4:
        msgs = [
            "😅 Boshlanishi qiyin bo‘lsa ham, keyingi safar ancha yaxshi chiqadi!",
            "🤔 Ehtimol, yana urinib ko‘rish kerakdir?",
            "🔁 Bu safar unchalik emas, lekin keyingi urinishda baland natija kutayapman sizdan!",
        ]
    elif 5 <= correct <= 10:
        msgs = [
            "👍 Yaxshi natija! Lekin hali ham imkoniyat bor.",
            "🚀 O‘rtadan oshdingiz, endi yuqoriga intiling!",
            "💡 Bilimingiz yaxshi ekan, yana urinib ko‘rsangiz mukammal bo‘ladi.",
        ]
    elif 11 <= correct <= 16:
        msgs = [
            "🔥 Zo‘r ishladingiz! Yana biroz kuchaysa, rekord sizniki bo‘ladi!",
            "👏 Bilim darajangiz baland ekan, barakalla!",
            "🏅 Juda yaxshi! Keyingi safar eng yuqori bosqichga chiqishingiz aniq.",
        ]
    elif 17 <= correct <= 19:
        msgs = [
            "🏆 Devorni sindirishga oz qoldi, zo‘r natija!",
            "🌟 Sizga salgina yetishmadi xolos, keyingi safar albatta 20/20 bo‘ladi!",
            "🎯 Ajoyib natija, siz bilimdonlar orasidasiz!",
        ]
    else:
        # maksimal (perfect game)
        if total and correct == total:
            msgs = [
                "👑 Geniy! Siz hamma savolni to‘g‘ri topdingiz!",
                "🥳 Mukammal! Sizdan kuchlisi yo‘q!",
                "💎 Siz haqiqiy yulduz! 20/20 — bu rekord!",
                "🔥 Bu ajoyib! Siz super-intellekt ekansiz!",
            ]
        else:
            # fallback
            msgs = ["💪 Yaxshi davom eting!"]

    return random.choice(msgs)


def _progress_header(data: dict) -> str:
    """Har savolda yuqoriga qisqa statistikani chiqarish."""
    step = data["i"] + 1  # 1-based
    total = len(data["qids"])
    correct = data["correct"]
    per = data["per"]
    start_balance = data.get("start_balance", Decimal("0.00"))

    earned_so_far = per * Decimal(correct)

    header = f"""
🎮 <b>TEST BOSHLANDI!</b> ({step}/{total})  
_________________________
⭐️ To‘g‘ri: {correct}  
💎 Bonus: {earned_so_far}  
💳 Balans: {start_balance + earned_so_far}
_________________________
"""
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
    # buttons.append([InlineKeyboardButton("🏁 Yakunlash va balansga o'tkazish", callback_data="tb_finish")])
    # is_last = (i + 1 == len(qids))
    # if is_last:  # faqat oxirgi savolda chiqaramiz
    #     buttons.append([InlineKeyboardButton("🏁 Yakunlash va balansga o'tkazish", callback_data="tb_finish")])

    kb = InlineKeyboardMarkup(buttons)

    # Matn: progress + savol
    header = _progress_header(data)
    text = f"{header}\n🔮 Sirli savol: {q.text}"

    if update.callback_query:
        update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

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
        "since_credit_correct": 0,  # 🔹 checkpoint hisoblagichi
        "since_credit_total": 0,
        "since_credit_earned": Decimal("0.00"),
        "auto_every": s.auto_cashout_every_correct or 0,  # 0 => o'chirilgan
    }

    intro = f"""
🎲 <b>TEST BOSHLANDI!</b>
_______________________
📊 Savollar: {len(qids)} ta
💎 Har to‘g‘ri javob: {s.per_correct_bonus}
🎁 Hammasi to‘g‘ri bo‘lsa: {s.full_completion_bonus}
💰 Avto-cashout: har {s.auto_cashout_every_correct or 0} ta to‘g‘ri
"""

    # reply_keyboard text="Menyuga qaytish ⬅️" tugmasi bilan
    back_to_menu = ReplyKeyboardMarkup(
        [["Menyuga qaytish ⬅️"]],
        resize_keyboard=True,
    )

    if update.message:
        update.message.reply_html(intro, reply_markup=back_to_menu)
    else:
        update.callback_query.edit_message_text(intro, parse_mode="HTML")

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

    orig_idx = int(parts[2])
    data["since_credit_total"] += 1
    if orig_idx == 1:
        data["correct"] += 1
        data["since_credit_correct"] += 1
        # joriy topilgan delta (per * 1)
        data["since_credit_earned"] += data["per"]

        # CHECKPOINT: har N to'g'ri javobda avtomatik balansga yozish
        auto_every = data.get("auto_every", 0)
        if auto_every and data["since_credit_correct"] >= auto_every:
            user = CustomUser.objects.filter(chat_id=update.effective_user.id).first()
            delta_correct = data["since_credit_correct"]
            delta_total = data["since_credit_total"]
            # delta_total = delta_correct  # har to‘g‘ri topilganda ayni savol uchun jami +1 deb qabul qilamiz
            earned = data["since_credit_earned"]

            flush_partial_to_db(user, delta_correct, delta_total, earned)

            # start_balance ni real-time yangilaymiz
            data["start_balance"] += earned
            # nolga qaytaramiz
            data["since_credit_correct"] = 0
            data["since_credit_total"] = 0
            data["since_credit_earned"] = Decimal("0.00")

            # foydalanuvchiga xabar
            try:
                # ✅ to'liq xabar sifatida yuboramiz (toast emas)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"✅ Hisobingizga {earned} qo‘shildi (avto-cashout)."
                )
            except Exception:
                pass

    # keyingi savolga o'tish
    data["i"] += 1
    context.user_data["tb"] = data
    return _send_next(update, context)


def on_finish_now(update: Update, context: CallbackContext) -> int:
    """Foydalanuvchi istalgan payt '🏁 Yakunlash'ni bossin."""
    return _finish(update, context)


def _finish(update: Update, context: CallbackContext) -> int:
    user = CustomUser.objects.filter(chat_id=update.effective_user.id).first()
    data = context.user_data.get("tb") or {}

    correct = int(data.get("correct", 0))
    total = len(data.get("qids", []))
    per = data.get("per", Decimal("0.00"))
    full = data.get("full", Decimal("0.00"))
    start_balance = data.get("start_balance", Decimal("0.00"))

    # avval checkpointda qolgan qoldiq bo'lsa — DBga o'tkazib yuboramiz
    leftover_correct = data.get("since_credit_correct", 0)
    leftover_total = data.get("since_credit_total", 0)
    leftover_earned = data.get("since_credit_earned", Decimal("0.00"))
    if leftover_correct or leftover_total:
        # delta_total ni leftover_correct deb olaylik
        flush_partial_to_db(user, leftover_correct, leftover_total, leftover_earned)
        start_balance += leftover_earned

    # 2) Full-completion bonus (faqat hammasi to‘g‘ri bo‘lsa)
    final_full_bonus = full if (total and correct == total) else Decimal("0.00")
    if final_full_bonus:
        flush_partial_to_db(user, 0, 0, final_full_bonus)
        start_balance += final_full_bonus

    mot = motivational_text(correct, total)

    result_text = f"""
<b>✅ TEST YAKUNLANDI!</b>
_______________________
📊 Umumiy savollar: {total}ta
✅ To‘g‘ri javoblar: {correct}
💎 Yig‘ilgan bonus: +{leftover_earned}
💳 Balansingiz: {start_balance}
_______________________
<code>{mot}</code>
"""
    if update.callback_query:
        update.callback_query.answer()
        update.callback_query.delete_message()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyword.base(),
        )
    else:
        update.message.reply_html(result_text, reply_markup=keyword.base())

    context.user_data.pop("tb", None)
    return state.START
