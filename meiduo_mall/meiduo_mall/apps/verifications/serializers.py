from rest_framework import serializers
from django_redis import get_redis_connection
from redis import RedisError
import logging


# 日志记录器
logger = logging.getLogger('django')


class ImageCodeCheckSerializer(serializers.Serializer):
    """图片验证码序列化器"""

    # 定义待校验的字典：定义的字段名字，必须和外界传入的一致
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        """对比服务图片验证码和客户端传入图片验证码"""

        # 取出经过字段校验后的数据
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 使用image_code_id查询出redis中存储的图片验证码
        redis_conn = get_redis_connection('verify_codes')
        image_code_server = redis_conn.get('img_%s' % image_code_id)
        if image_code_server is None:
            raise serializers.ValidationError('无效图片验证码')

        # 在获取到image_code_server之后，对比text之前
        # 删除Redis图片验证码：防止暴力测试
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        # 对比客户端和服务器的验证阿妈
        # 因为py3中的redis，存储的数据都是bytes类型的，而在读取时也是保持原始的bytes类型，因为快
        image_code_server = image_code_server.decode()
        if text.lower() != image_code_server.lower():
            raise serializers.ValidationError('输入图片验证码有误')

        # 删除Redis图片验证码：如果比较一致失败，无法删除

        # 校验60s内是否重复发送短信验证码
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信验证码过于频繁')

        return attrs
