from django.contrib import admin
from .models import CustomUser, Channel

admin.site.register(CustomUser)
admin.site.register(Channel)
