from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import UserFav
from goods.serializer import GoodsSerializer


class UserFavDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ['goods', 'id']


class UserFavSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        # ToDo items belong to a parent list, and have an ordering defined
        # by the 'position' field. No two items in a given list may share
        # the same position.
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=['goods', 'user']
            )
        ]
        model = UserFav
        fields = ['goods', 'user', 'id']
