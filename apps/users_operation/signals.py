from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserFav

# 商品收藏数量可以用信号量来监听UserFav的操作来实现
@receiver(post_save, sender=UserFav)
def create_handler(sender, instance=None, created=None, **kwargs):
    if created:
        good = instance.goods
        good.fav_num += 1
        good.save()


@receiver(post_delete, sender=UserFav)
def create_handler(sender, instance=None, **kwargs):
    good = instance.goods
    good.fav_num -= 1
    good.save()
