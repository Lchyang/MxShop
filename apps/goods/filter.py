from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Goods


class ProductFilter(filters.FilterSet):
    pricemax = filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    pricemin = filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    top_category = filters.NumberFilter(field_name='top_category', method='top_category_filters')

    def top_category_filters(self, queryset, name, value):
        return queryset.filter(
            Q(category_id=value) | Q(category__parent_category_id=value) | Q(
                category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['name', 'pricemax', 'pricemin', 'is_hot']
