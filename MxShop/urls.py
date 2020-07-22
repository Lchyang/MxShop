"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.static import serve
from django.urls import path, re_path, include

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.documentation import include_docs_urls
import xadmin

from MxShop.settings import MEDIA_ROOT
from goods.views import GoodsViewSet, CategoryViewSet, IndexCategoryVeiwSet
from users.views import SendSMSViewSet, UserViewSet
from users_operation.views import UserFavViewSet
from trade.views import ShoppingCartViewSet, OrderViewSet
from trade.views import AliPayView

router = DefaultRouter()
router.register(r'goods', GoodsViewSet, base_name='goods')
router.register(r'categorys', CategoryViewSet, base_name='categorys')
router.register(r'codes', SendSMSViewSet, base_name='codes')
router.register(r'users', UserViewSet, base_name='users')
router.register(r'userfavs', UserFavViewSet, base_name='user_favs')
router.register(r'shopcart', ShoppingCartViewSet, base_name='shop_cart')
router.register(r'order', OrderViewSet, base_name='order')
router.register(r'indexcategory', IndexCategoryVeiwSet, base_name='indexcategory')

urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    re_path(r'^docs/', include_docs_urls(title='慕学生鲜')),
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # rest_framework token 认证
    re_path(r'^api-token-auth', views.obtain_auth_token),
    # jwt token 认证
    re_path(r'^login', obtain_jwt_token),
    re_path(r'^alipay/return', AliPayView.as_view(), name="alipay")

]
