from django_filters import rest_framework as django_filters

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters as drf_filter
from rest_framework.pagination import PageNumberPagination

from .filter import ProductFilter
from .serializer import GoodsSerializer, CategorySerializer
from .models import Goods, GoodsCategory


# class GoodsListView(APIView):
#     def get(self, request, format=None):
#         goods = Goods.objects.all()
#         serializer = GoodsSerializer(goods, many=True)
#         return Response(serializer.data)

# APIView 只是对django view 进行简单的封装， genericsAPIView 进行了序列化，分页等操作
# mixin 对http的操作进行的封装
# ViewSet 对通过重写as_view 方法对路由实现了简化。
class GoodsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 10000


class GoodsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    filter_backends = (django_filters.DjangoFilterBackend, drf_filter.SearchFilter, drf_filter.OrderingFilter)
    search_fields = ['name', 'shop_price']
    ordering_fields = ['shop_price', 'add_time']
    filterset_class = ProductFilter


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
    获取商品列表

    retrieve:
    获取商品详情
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer
