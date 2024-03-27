import django_filters
from django_filters import DateFilter, CharFilter
from product.models import Product

class ProductFilter(django_filters.FilterSet):

    class Meta:
        model = Product
        fields = ['name', "supplier", "category","buy_price","sell_price"]
