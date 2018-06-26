import random
import logging

from rest_framework.generics import GenericAPIView

from . import serializers
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from libs.yuntongxun.sms import CCP
from . import constants
# Create your views here.

# 日志记录器
logger = logging.getLogger('django')


# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    """发送短信验证码"""
    # 指定序列化器
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 忽略校验
        # 创建序列化器对象
        data = request.query_params
        serializer = self.get_serializer(data=request.query_params)

        # 开启校验
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 存储短信到redis数据库
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],constants.SEND_SMS_TEMPLATE_ID)

        # 响应结果
        return Response({'message': 'OK'})

# url('^image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
class ImageCodeView(APIView):
    """提供图片验证码"""

    def get(self, request, image_code_id):
        # 生成图片验证码:text是验证码内容，需要保存到Redis；image是图片验证码数据，需要响应给前端
        text, image = captcha.generate_captcha()

        # 将图片验证码内容存储到redis数据库
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex('key', 'expires', 'value')
        redis_conn.setex('img_%s'%image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 将图片验证码图片数据响应到前端
        return HttpResponse(image, content_type='image/jpg')