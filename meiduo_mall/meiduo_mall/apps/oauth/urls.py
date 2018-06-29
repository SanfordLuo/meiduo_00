from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # 获取QQ扫码登录连接
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    # 用户扫码登录的回调处理
    url(r'^qq/user/$', views.QQAuthUserView.as_view()),

]