from django_filters import rest_framework as django_filters

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters as drf_filter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .filter import ProductFilter
from .serializer import (GoodsSerializer, CategorySerializer,
                         IndexCategorySerializer)
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


class GoodsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    """
    list:
    获取商品列表

    retrieve:
    获取商品详情
    """
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    filter_backends = (django_filters.DjangoFilterBackend,
                       drf_filter.SearchFilter, drf_filter.OrderingFilter)
    search_fields = ('=name', 'goods-brief', 'goods_desc')
    ordering_fields = ('shop_price', 'sold_num')
    filter_class = ProductFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    list:
    获取商品分类列表

    retrieve:
    获取商品分类详情
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer


class IndexCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
    首页商品列表展示
    """
    queryset = GoodsCategory.objects.filter(is_tab=True)
    serializer_class = IndexCategorySerializer
