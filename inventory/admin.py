from django.contrib import admin
from .models import Inventory, Category, Supplier, ReturnToSupplier


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Inventory)
admin.site.register(Supplier)
admin.site.register(ReturnToSupplier)
