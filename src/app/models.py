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


class Prices(models.Model):
    with_profile_1 = models.DecimalField(max_digits=10, decimal_places=2, help_text="Profilga kirish orqali 1-oy")
    with_profile_12 = models.DecimalField(max_digits=10, decimal_places=2, help_text="Profilga kirish orqali 12-oy")
    with_gift_3 = models.DecimalField(max_digits=10, decimal_places=2, help_text="Gift orqali 3-oy")
    with_gift_6 = models.DecimalField(max_digits=10, decimal_places=2, help_text="Gift orqali 6-oy")
    with_gift_12 = models.DecimalField(max_digits=10, decimal_places=2, help_text="Gift orqali 12-oy")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.with_profile_1)

    class Meta:
        verbose_name_plural = 'Premium narxlari'
        verbose_name = 'Premium narx'
        db_table = 'prices'


class StarsPrices(models.Model):
    price_50 = models.DecimalField(max_digits=10, decimal_places=2, help_text="50 Stars narxi")
    price_75 = models.DecimalField(max_digits=10, decimal_places=2, help_text="75 Stars narxi")
    price_100 = models.DecimalField(max_digits=10, decimal_places=2, help_text="100 Stars narxi")
    price_150 = models.DecimalField(max_digits=10, decimal_places=2, help_text="150 Stars narxi")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.price_50)

    class Meta:
        verbose_name_plural = 'Stars narxlari'
        verbose_name = 'Stars narx'
        db_table = 'star_prices'
