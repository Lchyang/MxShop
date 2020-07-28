import requests
import json
import os
import sys

from rest_framework.response import Response
from rest_framework.views import APIView


def get_data():
    res = requests.get(url="http://81.70.37.90/goods/?format=json")
    # print(res.text)
    h_data = json.loads(res.text)
    # print(data)
    results = h_data.get('results', None)
    print(results)
    return results


def handle_data(data):
    data['category'].pop('sub_cat')
    pop_list = ['goods_brief', 'goods_front_image', 'images', 'goods_desc']
    for pop_item in pop_list:
        data.pop(pop_item)
    return data


class HandelGoodsView(APIView):
    def get(self, request):
        ini_data = get_data()
        handled_data = handle_data(ini_data)
        print(handled_data)
        return Response(handled_data)


if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MxShop.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    print(get_data())
