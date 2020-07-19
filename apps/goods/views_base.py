from django.views.generic import View

from goods.models import Goods

class GoodsListView(View):
    def get(self, request):
        '''
        通过Django View 实现商品列表
        :param request:
        :return:
        '''
        json_list = []
        goods = Goods.objects.all()[:10]
        # for good in goods:
        #     json_dict = {}
        #     json_dict["name"] = good.name
        #     json_dict["category"] = good.category.name
        #     json_dict["market_price"] = good.market_price
        #     json_list.append(json_dict)
        #
        # from django.forms.models import model_to_dict
        from django.core import serializers

        json_data = serializers.serialize('json', goods)

        from django.http import HttpResponse
        import json

        return HttpResponse(json_data, content_type="application/json")