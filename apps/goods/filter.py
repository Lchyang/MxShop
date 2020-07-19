from django_filters import rest_framework as filters
from .models import Goods


class ProductFilter(filters.FilterSet):
    pricemax = filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    pricemin = filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    name = filters.CharFilter(field_name = 'name', lookup_expr='icontains')

    class Meta:
        model = Goods
        fields = ['name', 'pricemax', 'pricemin','is_hot']
