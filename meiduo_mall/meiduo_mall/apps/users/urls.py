from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views


urlpatterns = [
    # 校验用户名和手机号是否重复注册
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 注册
    url(r'^users/$', views.UserView.as_view()),
    # 封装好的登录序列化器
    url(r'^authorizations/$', obtain_jwt_token),
    # 提供登录用户的详情的
    url(r'^user/$', views.UserDetailView.as_view()),
    # 保存用户邮箱
    url(r'^email/$', views.EmailView.as_view()),
    # 邮箱验证
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),

]