from rest_framework import serializers

from .models import Area


class AreasSerializer(serializers.ModelSerializer):
    """list 行为的序列化器"""

    class Meta:
        # 指定输出的数据的模型类
        model = Area
        # 指定输出的字段
        fields = ('id', 'name')


class SubsAreasSerializer(serializers.ModelSerializer):
    """list 行为的序列化器"""

    # 关联
    subs = AreasSerializer(many=True, read_only=True)

    class Meta:
        # 指定输出的数据的模型类
        model = Area
        # 指定输出的字段
        fields = ('id', 'name', 'subs')
