from django.contrib import admin
from .models import *

admin.site.register(Transaction)
admin.site.register(Payment)
admin.site.register(Balance)
admin.site.register(Expense)
