from datetime import datetime

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.views import APIView

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

    # 通过购物车影响商品数量的逻辑
    def perform_create(self, serializer):
        instance = serializer.save()
        goods = instance.goods
        goods.goods_num -= instance.nums
        goods.save()

    def perform_update(self, serializer):
        shop_cart = ShoppingCart.objects.filter(id=serializer.instance.id)
        if shop_cart:
            shop_cart = shop_cart[0]
        pre_nums = shop_cart.nums
        instance = serializer.save()
        goods = instance.goods
        later_nums = instance.nums
        goods.goods_num -= (later_nums - pre_nums)
        goods.save()

    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()


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
        if order_goods:
            return order_goods


from utils.alipay import AliPay
from MxShop.settings import APP_PRIVATE_KEY_PATH, ALIPAY_PUBLIC_KEY_PATH, RETURN_URL, NOTIFY_URL
from rest_framework.response import Response


class AliPayView(APIView):

    @staticmethod
    def get(request):
        """
        处理支付宝return_url
        :param request:
        :return:
        """
        processed_query = {}
        for key, value in request.GET.items():
            processed_query[key] = value
        ali_sign = processed_query.pop("sign", None)

        alipay = AliPay(
            appid="2016102600761595",
            app_notify_url=NOTIFY_URL,
            app_private_key_path=APP_PRIVATE_KEY_PATH,
            alipay_public_key_path=ALIPAY_PUBLIC_KEY_PATH,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url=RETURN_URL,
        )

        verfiy = alipay.verify(processed_query, ali_sign)

        # 如果验证通过，将数据同步到数据库，更新订单状
        if verfiy is True:
            order_sn = processed_query.get("out_trade_no", None)
            pay_status = processed_query.get("trade_status", None)
            trade_no = processed_query.get("trade_no", None)
            exited_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for exited_order in exited_orders:
                exited_order.trade_no = trade_no
                exited_order.pay_status = pay_status
                exited_order.pay_time = datetime.now()
                exited_order.save()

            return Response("success")

    @staticmethod
    def post(request):
        """
        处理支付宝notify_url
        :param request:
        :return:
        """
        processed_query = {}
        for key, value in request.POST.items():
            processed_query[key] = value
        ali_sign = processed_query.pop("sign", None)

        alipay = AliPay(
            appid="2016102600761595",
            app_notify_url=NOTIFY_URL,
            app_private_key_path=APP_PRIVATE_KEY_PATH,
            alipay_public_key_path=ALIPAY_PUBLIC_KEY_PATH,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url=RETURN_URL,
        )
        verfiy = alipay.verify(processed_query, ali_sign)

        # 如果验证通过，将数据同步到数据库，更新订单状
        if verfiy is True:
            order_sn = processed_query.get("out_trade_no", None)
            pay_status = processed_query.get("trade_status", None)
            trade_no = processed_query.get("trade_no", None)
            exited_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for exited_order in exited_orders:
                order_goods = exited_order.order_goods.all()
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.goods_num -= order_good.goods_num
                    goods.save()
                exited_order.trade_no = trade_no
                exited_order.pay_status = pay_status
                exited_order.pay_time = datetime.now()
                exited_order.save()

            return Response("success")
