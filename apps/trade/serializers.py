import time
import random

from rest_framework import serializers
from .models import ShoppingCart
from .models import Goods, OrderGoods, OrderInfo
from goods.serializer import GoodsSerializer


class ShopingCartSerializer(serializers.Serializer):
    # 获取当前登录用户的user
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # Todo 外键many=True该不该加？queryset怎么起作用？，应该是一对一的关系不加many=True, 加上之后goods为列表
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())
    nums = serializers.IntegerField(required=True, min_value=1, error_messages={
        'required': '请选择商品购买数量',
        'min_value': '商品数量不能小于1'
    })

    # 当不使用serializers.ModelSerializer时要写create函数，用于当前端数据传入是序列化使用
    def create(self, validated_data):
        # serializers 中获取user, viewset可以直接self.user
        # 经过验证的数据存在validated_data中，没有验证过的数据在self.initial_data中
        user = self.context['request'].user
        goods = validated_data['goods']
        nums = validated_data['nums']
        exited = ShoppingCart.objects.filter(user=user, goods=goods)
        if exited:
            exited = exited[0]
            exited.nums += nums
            exited.save()
        else:
            exited = ShoppingCart.objects.create(**validated_data)

        return exited

    # 更新购物车
    def update(self, instance, validated_data):
        instance.nums = validated_data['nums']
        instance.save()
        return instance


class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShoppingCart
        goods_fields = '__all__'


class OrderInfoSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    order_sn = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    pay_status = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)

    def generate_order_sn(self):
        # 生成唯一订单号，当前时间+user.id+两位随机数
        order_sn = "{}{}{}".format(time.strftime("%Y%m%d%H%M%S", time.localtime()), self.context['request'].user.id,
                                   random.randint(10, 99))
        return order_sn

    def validate(self, attrs):
        attrs['order_sn'] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderInfoDetailSerializer(serializers.ModelSerializer):
    order_goods = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
