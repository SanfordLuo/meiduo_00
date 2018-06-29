from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import api_settings

from .utils import OAuthQQ
from . import serializers
from .exceptions import QQAPIException
from .models import OAuthQQUser
# Create your views here.



# url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
class QQAuthURLView(APIView):
    """提供QQ扫码登录界面的连接给用户"""

    def get(self, request):
        # 获取到next参数，实现将来从哪里进入的登录界面，QQ登录成功后就回到哪里
        next = request.query_params.get('next')

        # 创建QQ登录的工具对象
        oauth = OAuthQQ(state=next)

        # 生成QQ扫码登录的连接（逻辑）
        login_url = oauth.get_qq_login_url()

        return Response({'login_url': login_url})


# url(r'^qq/user/$', views.QQAuthUserView.as_view()),
class QQAuthUserView(GenericAPIView):
    """用户扫码登录的回调处理"""

    # 指定序列化器
    serializer_class = serializers.QQAuthUserSerializer

    def get(self, request):
        # 提取code请求参数
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'})

        # 创建qq登录的工具对象
        oauth = OAuthQQ()

        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_openid(access_token)
        except QQAPIException:
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 使用openid查询该QQ用户是否在美多商城中绑定过用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果openid没绑定美多商城用户，创建用户并绑定到openid
            access_token_openid = OAuthQQ.generate_save_user_token(openid)
            return Response({'access_token': access_token_openid})
        else:
            # 如果openid已绑定美多商城用户，直接生成JWT token，并返回
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # 获取关联openid的user
            user = oauth_user.user

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            # 向前端响应token, user_id,username
            return Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })

    def post(self, request):
        """给openid绑定用户数据"""

        # 获取序列化器：注册的数据都在POST请求的请求体里面
        serializer = self.get_serializer(data=request.data)
        # 开启校验
        serializer.is_valid(raise_exception=True)
        # 保存校验的数据 : create会返回user
        user = serializer.save()

        # 生成JWT token 响应
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 向前端响应token, user_id,username
        return Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })
