from rest_framework import serializers
from .models import Goods, GoodsCategory, GoodsImage, GoodsCategoryBrand, IndexAd
from django.db.models import Q


class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ('image',)


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = ImageSerializer(many=True)

    class Meta:
        model = Goods
        fields = '__all__'


class GoodsCategoryBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = '__all__'


# 首页布局中有分类，分类下面有子类，分类下面有商品品牌，分类下面有商品，三个一对多关系的序列化
class IndexCategorySerializer(serializers.ModelSerializer):
    brands = GoodsCategoryBrandSerializer(many=True)
    sub_cat = CategorySerializer2(many=True)
    goods = serializers.SerializerMethodField()
    ad_good = serializers.SerializerMethodField()

    def get_ad_good(self, obj):
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            ad_good = ad_goods[0]
            good = Goods.objects.filter(name=ad_good.goods)
            # 当序列化是一个查询集的时候也就是queryset的时候many=True
            good_serializer = GoodsSerializer(good, many=True, context={'request': self.context['request']})
            return good_serializer.data

    def get_goods(self, obj):
        goods = Goods.objects.filter(
            Q(category_id=obj.id) | Q(category__parent_category_id=obj.id) | Q(
                category__parent_category__parent_category_id=obj.id))
        goods_serializers = GoodsSerializer(goods, many=True, context={'request': self.context['request']})
        return goods_serializers.data

    class Meta:
        model = GoodsCategory
        fields = '__all__'
