from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import mixins

from utils.permissons import IsOwnerOrReadOnly
from .models import ShoppingCart, OrderGoods, OrderInfo
from .serializers import ShopingCartSerializer, ShopCartDetailSerializer, OrderInfoSerializer, \
    OrderInfoDetailSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    list:
    获取购物车列表
    create:
    添加购物车
    delete:
    删除购物车数据
    """
    serializer_class = ShopingCartSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'goods_id'

    # queryset or get_queryset 是list功能的参数
    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    # 当不同的操作使用不同的serializer时要重写get_serializer_class 方法
    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopingCartSerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        queryset = OrderInfo.objects.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderInfoDetailSerializer
        else:
            return OrderInfoSerializer

    # CreateModelMixin 重写perform_create函数，将订单详情，商品，商品数量生成order_goods 同时删除购物车数据
    def perform_create(self, serializer):
        global order_goods
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()

            shop_cart.delete()
        return order_goods
