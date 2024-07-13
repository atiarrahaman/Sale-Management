from django.contrib import admin
from .models import Product, Cart, CartProduct, Order, OrderProduct, ReturnProduct, DamageProduct



admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(OrderProduct)
admin.site.register(Order)
admin.site.register(ReturnProduct)
admin.site.register(DamageProduct)
