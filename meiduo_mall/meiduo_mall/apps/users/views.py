from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView

from . import serializers
# Create your views here.


# url(r'^users/$', views.UserView.as_view()),
class UserView(CreateAPIView):
    """注册"""

    serializer_class = serializers.CreateUserSerializer


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


# url(r'^user/$', views.UserDetailView.as_view()),
class UserDetailView(RetrieveAPIView):
    """提供登录用户的详情的"""

    # 指定序列化器
    serializer_class = serializers.UserDetailSerializer

    # IsAuthenticated 采用的是JWT的验证
    # 用户身份验证：是否是登录用户
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """返回当前谁是登录用户
        为什么要重写该方法:是因为我们的路由没有主键
        返回的user是JWT验证系统验证后的登录用户
        """
        return self.request.user
