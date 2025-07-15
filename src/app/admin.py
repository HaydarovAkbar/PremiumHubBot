from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Channel, Settings, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, \
    StoryBonusPrice, StoryBonusAccounts, Group, InvitedUser, InterestingBonus, InterestingBonusUser, CustomUserAccount, \
    SpendPrice, SpendPriceField, PromoCodes, TopUser, CustomPromoCode


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


@admin.register(CustomPromoCode)
class CustomPromoCodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'count', 'status', 'reward', 'created_at']
    search_fields = ['name',]
    list_per_page = 20
    list_filter = ['status',]