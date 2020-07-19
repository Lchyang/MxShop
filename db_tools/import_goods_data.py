import os
import sys

pwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(pwd)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MxShop.settings')

import django
django.setup()

from goods.models import Goods, GoodsCategory, GoodsImage

from db_tools.data.product_data import row_data

for good in row_data:
    good_instance = Goods()
    good_instance.name = good['name']
    good_instance.goods_desc = good['goods_desc'] if good['goods_desc'] is not None else ''
    good_instance.market_price = good['market_price'].replace('￥', '').replace('元', '')
    good_instance.shop_price =  good['sale_price'].replace('￥', '').replace('元', '')
    good_instance.goods_brief = good['desc'] if good['desc'] is not None else ''
    good_instance.goods_front_image = good['images'][0] if good['images'] else ''

    category_name = good['categorys'][-1]
    category = GoodsCategory.objects.filter(name = category_name)
    if category:
        good_instance.category = category[0]
    good_instance.save()

    for image in good['images']:
        good_image = GoodsImage()
        good_image.image = image
        good_image.goods = good_instance
        good_image.save()



