from django.db import models
from django.contrib.auth.models import User


class CustomUser(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=14, null=True, blank=True)
    device_hash = models.CharField(max_length=64, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'custom_user'


class Channel(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'channel'


class Group(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    link = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'group'


class Settings(models.Model):
    device_count = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.device_count)

    class Meta:
        db_table = 'settings'