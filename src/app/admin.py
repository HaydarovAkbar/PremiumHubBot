from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Channel, Settings, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, \
    StoryBonusPrice, StoryBonusAccounts, Group, InvitedUser, InterestingBonus, InterestingBonusUser, CustomUserAccount, \
    SpendPrice, SpendPriceField, PromoCodes, TopUser, CustomPromoCode, CustomUserPromoCode, GlobalTestSettings, Question, Quiz, UserAnswer

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'is_active', 'is_blocked', 'invited_count']
    list_filter = ['is_active', 'is_blocked', 'is_admin']
    list_per_page = 20
    search_fields = ['chat_id', 'phone_number']
    search_help_text = "chat_id, phone_number"

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('first_name', 'last_name', 'phone_number', 'is_active', 'is_blocked', 'is_admin', 'username')
        }),
        ("Qo'shimcha ma'lumotlar", {
            'fields': ('chat_id', 'device_hash', 'invited_count', 'premium_count', 'referral')
        }),
    )

    add_fieldsets = (
        ("Asosiy ma'lumotlar", {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone_number', 'is_active', 'is_blocked')
        }),
    )


class CustomUserAccountAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'current_price']
    search_fields = ['chat_id', ]
    list_per_page = 20


class SettingsAdmin(admin.ModelAdmin):
    list_display = ['device_count', 'spend_price', 'referral_price', 'referral_prem_price', 'is_active']


class SpendPriceFieldAdmin(admin.ModelAdmin):
    list_display = ['spend_price', 'name', 'price']


class PricesAdmin(admin.ModelAdmin):
    list_display = ['with_profile_1', 'with_profile_12', 'with_gift_3', 'with_gift_6', 'with_gift_12',
                    'is_active']


class StarsPricesAdmin(admin.ModelAdmin):
    list_display = ['price_50', 'price_75', 'price_100', 'price_150', 'created_at',
                    'is_active']


class DailyBonusAdmin(admin.ModelAdmin):
    list_display = ['rewards_channel', 'chat_id', 'last_bonus', 'created_at',
                    'is_active']
    search_fields = ['chat_id', ]


class ChannelAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'name', 'link', 'created_at',
                    'is_active']


class GroupAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'name', 'link', 'price', 'limit', 'created_at',
                    'is_active']


class InvitedUserAdmin(admin.ModelAdmin):
    list_display = ['inviter_chat_id', 'new_user_chat_id', 'created_at']
    list_per_page = 20
    search_fields = ['inviter_chat_id', 'new_user_chat_id']
    search_help_text = "inviter_chat_id, inviter_chat_id"

class PromoCodesAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat_id', 'created_at', 'reward',
                    'status']
    search_fields = ['chat_id', ]
    search_help_text = 'chat_id kiriting'
    list_per_page = 20


class TopUserAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'fullname', 'weekly_earned', 'monthly_earned', 'balance',
                    'total_earned', 'created_at']
    search_fields = ['chat_id', ]
    search_help_text = 'chat_id kiriting'
    list_per_page = 20


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Settings, SettingsAdmin)
admin.site.register(Prices, PricesAdmin)
admin.site.register(StarsPrices, StarsPricesAdmin)
admin.site.register(RewardsChannelBoost)
admin.site.register(DailyBonus, DailyBonusAdmin)
admin.site.register(StoryBonusPrice)
admin.site.register(StoryBonusAccounts)
admin.site.register(Group, GroupAdmin)
admin.site.register(InvitedUser, InvitedUserAdmin)
admin.site.register(InterestingBonus)
admin.site.register(InterestingBonusUser)
admin.site.register(CustomUserAccount, CustomUserAccountAdmin)
admin.site.register(SpendPrice)
admin.site.register(SpendPriceField, SpendPriceFieldAdmin)
admin.site.register(PromoCodes, PromoCodesAdmin)
admin.site.register(TopUser)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(UserAnswer)


@admin.register(CustomPromoCode)
class CustomPromoCodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'count', 'status', 'reward', 'created_at']
    search_fields = ['name',]
    list_per_page = 20
    list_filter = ['status',]


@admin.register(CustomUserPromoCode)
class CustomUserPromoCodeAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'promo_code', 'created_at']
    search_fields = ['chat_id', 'promo_code__name']
    list_per_page = 20


@admin.register(GlobalTestSettings)
class GlobalTestSettingsAdmin(admin.ModelAdmin):
    list_display = ("question_limit", "per_correct_bonus", "full_completion_bonus",
                    "time_limit_seconds", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    # Changelist sahifasiga kirganda avtomatik ravishda bitta mavjud obyektning
    # change form’iga redirect qilamiz (yoki Add sahifasiga yuboramiz)
    def changelist_view(self, request, extra_context=None):
        qs = GlobalTestSettings.objects.all()
        if qs.exists():
            obj = qs.first()
            url = reverse("admin:app_globaltestsettings_change", args=[obj.pk])
            return HttpResponseRedirect(url)
        else:
            # Hech narsa bo‘lmasa — Add sahifasiga yuboramiz
            url = reverse("admin:app_globaltestsettings_add")
            return HttpResponseRedirect(url)

    # Yozuv allaqachon bo‘lsa, yana “Add” qilishga ruxsat bermaymiz
    def has_add_permission(self, request):
        return not GlobalTestSettings.objects.exists()

    # O‘chirib yuborishni odatda taqiqlaymiz (xohlasangiz True qiling)
    def has_delete_permission(self, request, obj=None):
        return False

    # Ixtiyoriy: faqat bitta obyekt ko‘rsatilgani uchun “list view” menyulari keraksiz
    def get_model_perms(self, request):
        # Model admin menyuda ko‘rinishida davom etadi.
        # Agar menyuda umuman ko‘rinmasin desangiz, bo‘sh dict qaytaring.
        return super().get_model_perms(request)