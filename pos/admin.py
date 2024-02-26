from django.contrib import admin
from .models import Client,Pos,Checkout,Payment_type
# Register your models here.
admin.site.register(Client)
admin.site.register(Pos)
admin.site.register(Checkout)
admin.site.register(Payment_type)
