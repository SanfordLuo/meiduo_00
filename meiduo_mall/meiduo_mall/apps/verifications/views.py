from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from . import constants
# Create your views here.


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