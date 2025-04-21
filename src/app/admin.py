from django.contrib import admin
from .models import CustomUser, Channel, Settings, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, \
    StoryBonusPrice, StoryBonusAccounts, Group, InvitedUser, InterestingBonus, InterestingBonusUser, CustomUserAccount, \
    SpendPrice, SpendPriceField

admin.site.register(CustomUser)
admin.site.register(Channel)
admin.site.register(Settings)
admin.site.register(Prices)
admin.site.register(StarsPrices)
admin.site.register(RewardsChannelBoost)
admin.site.register(DailyBonus)
admin.site.register(StoryBonusPrice)
admin.site.register(StoryBonusAccounts)
admin.site.register(Group)
admin.site.register(InvitedUser)
admin.site.register(InterestingBonus)
admin.site.register(InterestingBonusUser)
admin.site.register(CustomUserAccount)
admin.site.register(SpendPrice)
admin.site.register(SpendPriceField)
