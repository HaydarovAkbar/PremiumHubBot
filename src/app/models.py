from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# class CustomUserManager(BaseUserManager):
#     def create_user(self, username, email, password=None):
#         if not email:
#             raise ValueError('The Email field must be set')
#         user = self.model(username=username, email=email)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, username, email, password=None):
#         user = self.create_user(username, email, password)
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user


class CustomUser(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=14, null=True, blank=True)
    device_hash = models.CharField(max_length=64, null=True, blank=True)
    invited_count = models.PositiveIntegerField(default=0)
    premium_count = models.PositiveIntegerField(default=0)
    referral = models.BigIntegerField(default=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    # objects = CustomUserManager()
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return f"({self.first_name} {self.last_name}) - Phone: {self.phone_number}   -  is_blocked: {self.is_blocked}"

    class Meta:
        verbose_name_plural = "Foydalanuvchilar"
        verbose_name = "Foydalanuvchi"
        db_table = 'custom_user'


class Channel(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Majburiy azolik kanallari"
        verbose_name = "Majburiy azolik kanal"
        db_table = 'channel'


class Group(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True,
                                verbose_name="Qo'shganlik uchun summa: ")
    limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="Qo'shish kerak bo'lgan limit")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Azolik gruppasi"
        verbose_name = "Azolik gruppasi"
        db_table = 'group'


class Settings(models.Model):
    device_count = models.IntegerField(default=1)
    spend_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    referral_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Referral summasi", default=0)
    referral_prem_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Referral premium summasi",
                                              default=0)
    promo_limit = models.IntegerField(null=True, blank=True, verbose_name="Promo limit")

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.device_count)

    class Meta:
        verbose_name_plural = "Asosiy sozlamalar"
        verbose_name = "Asosiy sozlama"
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


class RewardsChannelBoost(models.Model):
    channel_url = models.CharField(max_length=150, null=True, blank=True, verbose_name='Ovoz beriladigan kanal')
    elementary_bonus = models.DecimalField(max_digits=10, decimal_places=2, help_text="Boshlang'ich bonus narxi",
                                           null=True, blank=True)
    daily_bonus = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Kunlik bonus narxi",
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.channel_url)


class DailyBonus(models.Model):
    rewards_channel = models.OneToOneField(RewardsChannelBoost, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_bonus = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.chat_id)

    class Meta:
        verbose_name_plural = 'Kunlik bonuslar'
        verbose_name = 'Kunlik bonus'
        db_table = 'daily_bonus'
        indexes = [
            models.Index(fields=['chat_id', 'rewards_channel']),
        ]


class StoryBonusPrice(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Boshlang'ich bonus narxi",
                                null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.price)

    class Meta:
        verbose_name_plural = 'Story narxlar'
        verbose_name = 'Story narx'
        db_table = 'story_bonus_price'


class StoryBonusAccounts(models.Model):
    chat_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.chat_id)

    class Meta:
        verbose_name_plural = 'Story bonuslar'
        verbose_name = 'Story bonuslar'
        db_table = 'story_bonus'


class CustomUserAccount(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Jami summasi", default=0)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Hozirgi summasi", default=0)

    def __str__(self):
        return str(self.chat_id) + ' <---> ' + str(self.current_price)


class InvitedUser(models.Model):
    inviter_chat_id = models.BigIntegerField(null=True, blank=True)
    new_user_chat_id = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.inviter_chat_id)

    class Meta:
        verbose_name_plural = 'Gruppaga qo\'shilganlar'
        verbose_name = 'Gruppaga qo\'shganlar'
        db_table = 'invited_user'


class InvitedBonusUser(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    clean = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.chat_id)

    class Meta:
        verbose_name_plural = 'Gruppaga qo\'shilganlar bonuslari'
        verbose_name = 'Gruppaga qo\'shilganlar bonuslar'
        db_table = 'invited_user_bonus'


class InterestingBonus(models.Model):
    bio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Bio summasi")
    fullname = models.DecimalField(max_digits=10, decimal_places=2, help_text="Nikname summasi")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.bio) + " - " + str(self.fullname)

    class Meta:
        verbose_name_plural = 'Qiziqarli bonus narxlari'
        verbose_name = 'Qiziqarli bonus narx'
        db_table = 'interesting_bonus'


class InterestingBonusUser(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    bio = models.BooleanField(default=False)
    fullname = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.chat_id)

    class Meta:
        verbose_name_plural = 'Qiziqarli bonus userlar'
        verbose_name = 'Qiziqarli bonus user'
        db_table = 'interesting_user_bonus'


class SpendPrice(models.Model):
    text = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.text)[:20]

    class Meta:
        verbose_name_plural = 'Sotish xabarlari'
        verbose_name = 'Sotish xabar'
        db_table = 'spend_price'


class SpendPriceField(models.Model):
    spend_price = models.ForeignKey(SpendPrice, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=120, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.spend_price)

    class Meta:
        verbose_name_plural = 'Sotish xabari narxlari'
        verbose_name = 'Sotish xabar narx'
        db_table = 'spend_price_field'


class PromoCodes(models.Model):
    name = models.CharField(max_length=14, null=True, blank=True)
    chat_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.BooleanField(default=False)

    reward = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = 'Promo kodlar'
        verbose_name = 'Promo kod'
        db_table = 'promo_codes'


class TopUser(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    balance = models.BigIntegerField(default=0)

    total_earned = models.BigIntegerField(default=0)

    weekly_earned = models.BigIntegerField(default=0)
    monthly_earned = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fullname} - {self.balance} so'm"

    class Meta:
        verbose_name_plural = 'Top userlar'
        verbose_name = 'Top user'
        db_table = 'top_user'
