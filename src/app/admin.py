from django.contrib import admin
from .models import CustomUser, Channel, Settings, Prices, StarsPrices

admin.site.register(CustomUser)
admin.site.register(Channel)
admin.site.register(Settings)
admin.site.register(Prices)
admin.site.register(StarsPrices)
