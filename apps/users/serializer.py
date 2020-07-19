import re
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import VerifyCode, UserProfile
from MxShop.settings import REGEX_MOBILE

User = get_user_model()


class VerifyMobileSerializer(serializers.Serializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    mobile = serializers.CharField(max_length=11)

    @staticmethod
    def validate_mobile(mobile):
        # 验证手机号码
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")

        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号非法")

        one_minute_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_minute_ago, mobile=mobile).count():
            raise serializers.ValidationError("距离上次一发送未超过一分钟")

        return mobile


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'gender', 'birthday', 'email', 'mobile']


class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(allow_blank=True, write_only=True, allow_null=True, max_length=4, min_length=4)
    username = serializers.CharField(required=True, allow_blank=False,
                                     validators=[UniqueValidator(User.objects.all(), message='用户已经存在')])
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True
    )

    # django 存储密码加密
    def create(self, validated_data):
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_code(self, code):
        verify_code = VerifyCode.objects.filter(mobile=self.initial_data['username']).order_by('-add_time')
        if verify_code:
            last_recode = verify_code[0]
            five_min_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if last_recode.add_time < five_min_ago:
                raise serializers.ValidationError('验证码过期')
            if last_recode.code != code:
                raise serializers.ValidationError('验证码错误')
        else:
            raise serializers.ValidationError('验证码错误')

    def validate(self, attrs):
        attrs['mobile'] = attrs['username']
        del attrs['code']
        return attrs

    class Meta:
        model = UserProfile
        fields = ['username', 'code', 'mobile', 'password']
