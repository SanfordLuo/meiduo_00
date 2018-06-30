from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from . import serializers





# Create your views here.

# GET /areas/  ==> list
# GET /areas/<pk>/  ==? retrieve
class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """提供省市区三级联动数据"""

    # 禁用分页
    pagination_class = None

    def get_queryset(self):
        """根据请求的行为，过滤不同的行为对应的序列化器需要的数据"""
        if self.action == 'list':
            return Area.objects.filter(parent=None)  # parent=None 是省级数据
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """根据请求的行为，指定不同的序列化器"""
        if self.action == 'list':
            return serializers.AreasSerializer
        else:
            return serializers.SubsAreasSerializer
