from django.contrib import admin
from .models import Product, Category


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Product)
admin.site.register(Category, CategoryAdmin)
