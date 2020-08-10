from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserProfile(AbstractUser):
    """
    用户
    """
    # verbose_name 作用 在admin后天管理系统中显示字段名称
    # null=True blank=True 区别， null表示数据库层面可以传入空值，blank表示前端传递参数可以为空值
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="手机号")
    gender = models.CharField(max_length=6, choices=(("male", "男"), ("female", "女")), default="female")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        if self.name is None:
            return self.username
        return self.name


class VerifyCode(models.Model):
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    code = models.CharField(max_length=10, verbose_name="验证码")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "短信验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code
