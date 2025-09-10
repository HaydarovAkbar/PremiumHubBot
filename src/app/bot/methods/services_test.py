# quiz/services_test.py
from __future__ import annotations
import random
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from app.models import (
    GlobalTestSettings,
    Quiz,
    Question,
    UserAnswer,
    CustomUser,
    CustomUserAccount,
    TopUser,
)

def get_starting_balance(user) -> Decimal:
    acc = CustomUserAccount.objects.filter(chat_id=user.chat_id).first()
    return acc.current_price if acc else Decimal("0.00")


# ======== SETTINGS ========

def get_settings() -> GlobalTestSettings:
    s = GlobalTestSettings.objects.first()
    if not s:
        s = GlobalTestSettings.objects.create()
    return s

# ======== LIMIT TEKSHIR + URINISHNI RO'YXATGA OLISH ========

def _get_or_create_ua(user: CustomUser) -> UserAnswer:
    ua, _ = UserAnswer.objects.get_or_create(user=user)
    return ua

def _reset_daily_if_needed(ua: UserAnswer) -> None:
    today = timezone.now().date()
    if ua.daily_attempts_date != today:
        ua.daily_attempts_date = today
        ua.daily_attempts = 0

def can_start_test(user: CustomUser) -> tuple[bool, str | GlobalTestSettings]:
    """
    Global sozlamalar va UserAnswer dagi kunlik/umumiy limitlar bo‘yicha ruxsatni tekshiradi.
    """
    settings = get_settings()
    ua = _get_or_create_ua(user)
    _reset_daily_if_needed(ua)

    if settings.max_attempts_per_user and ua.total_attempts >= settings.max_attempts_per_user:
        return False, "Maksimal urinishlar sonidan oshib ketdingiz."

    if settings.daily_attempt_limit and ua.daily_attempts >= settings.daily_attempt_limit:
        return False, "Bugungi urinishlar limitidan oshib ketdingiz."

    return True, settings

def register_attempt_start(user: CustomUser) -> UserAnswer:
    """
    Testni boshlayotganda 1 marta chaqiriladi: urinish counterlarini yangilaydi (DB).
    """
    ua = _get_or_create_ua(user)
    _reset_daily_if_needed(ua)
    ua.total_attempts = F('total_attempts') + 1
    ua.daily_attempts = F('daily_attempts') + 1
    ua.save(update_fields=["total_attempts", "daily_attempts", "daily_attempts_date", "updated_at"])
    ua.refresh_from_db(fields=["total_attempts", "daily_attempts", "daily_attempts_date"])
    return ua

# ======== SAVOLLARNI TANLASH ========

def pick_random_question_ids(limit: int, only_active: bool = True) -> list[int]:
    """
    Bir nechta quiz’lardan (default: faqat is_active=True) limit bo‘yicha random savollar.
    """
    qs = Question.objects.all()
    if only_active:
        qs = qs.filter(quiz__is_active=True)
    ids = list(qs.values_list("id", flat=True))
    if not ids:
        return []
    k = min(limit, len(ids))
    return random.sample(ids, k)

# ======== BONUS HISOBI ========

def compute_bonus(correct: int, total: int, per_correct_bonus: Decimal, full_completion_bonus: Decimal) -> Decimal:
    earned = per_correct_bonus * Decimal(correct)
    if total and correct == total:
        earned += full_completion_bonus
    return earned

# ======== YAKUNDA BARCHASINI DB'ga YOZISH ========


@transaction.atomic
def flush_partial_to_db(user: CustomUser, delta_correct: int, delta_total: int, earned: Decimal) -> None:
    """Sessiya tugamasdan turib, topilgan bonusning bir qismini balansga o'tkazish."""
    # 1) UserAnswer aggregatga qo‘shamiz
    ua, _ = UserAnswer.objects.select_for_update().get_or_create(user=user)
    ua.correct_count += delta_correct
    ua.total_count += delta_total
    ua.save(update_fields=["correct_count","total_count","updated_at"])

    # 2) Foydalanuvchi account
    acc, _ = CustomUserAccount.objects.select_for_update().get_or_create(chat_id=user.chat_id)
    acc.current_price += earned
    acc.total_price += earned
    acc.save(update_fields=["current_price","total_price"])

    # 3) TopUser
    tu, _ = TopUser.objects.select_for_update().get_or_create(
        chat_id=user.chat_id,
        defaults={"fullname": f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip()}
    )
    int_earned = int(earned)
    tu.balance += int_earned
    tu.total_earned += int_earned
    tu.weekly_earned += int_earned
    tu.monthly_earned += int_earned
    tu.save(update_fields=["balance","total_earned","weekly_earned","monthly_earned","updated_at"])