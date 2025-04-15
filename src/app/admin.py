from django.contrib import admin
from .models import TGUsers, Channel, Admin, Reklama, Stats, Category, Products, Order, OrderItem, Supplier, SupplierPrice, Caption, Boss, ProductSize

admin.site.register(TGUsers)
admin.site.register(Channel)
admin.site.register(Admin)
admin.site.register(Reklama)
admin.site.register(Stats)
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Supplier)
admin.site.register(SupplierPrice)
admin.site.register(Caption)
admin.site.register(Boss)
admin.site.register(ProductSize)