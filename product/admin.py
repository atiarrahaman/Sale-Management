from django.contrib import admin
from .models import Product, Category,Cart,CartProduct,Order,OrderProduct


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Product)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(OrderProduct)
admin.site.register(Order)
