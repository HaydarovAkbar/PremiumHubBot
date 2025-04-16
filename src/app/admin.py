from django.contrib import admin
from .models import CustomUser, Channel, Settings

admin.site.register(CustomUser)
admin.site.register(Channel)
admin.site.register(Settings)
