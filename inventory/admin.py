from django.contrib import admin
from .models import Inventory, Category, Supplier, ReturnToSupplier, Brand


class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Inventory)
admin.site.register(Supplier)
admin.site.register(ReturnToSupplier)
