from django.contrib import admin
from .models import CustomUser, Channel, Settings, Prices, StarsPrices, RewardsChannelBoost, DailyBonus, StoryBonusPrice, StoryBonusAccounts

admin.site.register(CustomUser)
admin.site.register(Channel)
admin.site.register(Settings)
admin.site.register(Prices)
admin.site.register(StarsPrices)
admin.site.register(RewardsChannelBoost)
admin.site.register(DailyBonus)
admin.site.register(StoryBonusPrice)
admin.site.register(StoryBonusAccounts)