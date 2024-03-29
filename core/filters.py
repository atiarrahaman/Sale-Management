import django_filters
from django_filters import DateFilter, CharFilter
from product.models import Product
from .models import Staff
from django.contrib.auth.models import User


class StaffFilter(django_filters.FilterSet):

    class Meta:
        model = User
        fields = ['username', "first_name", "last_name", "email"]
