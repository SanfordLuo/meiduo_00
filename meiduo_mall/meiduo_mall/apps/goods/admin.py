from django.contrib import admin

# Register your models here.

from . import models


class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """
        后台站点点击了保存按钮时会自动调用
        :param request: 本次保存的请求对象
        :param obj: 本次保存所操作的模型对象，对于这个需求，这里的obj==sku
        :param form: 本次保存的表单
        :param change: 本次保存的变化的数据
        :return: None
        """
        obj.save() # 父类自己的save方法，直接重写即可

        # 触发异步任务
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


class SKUSpecificationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


# class GoodsCategoryAdmin(admin.ModelAdmin):
#     """商品分类静态化l"""
#     def save_model(self, request, obj, form, change):
#         obj.save()
#         from celery_tasks.html.tasks import generate_static_list_search_html
#         generate_static_list_search_html.delay()
#
#     def delete_model(self, request, obj):
#         obj.delete()
#         from celery_tasks.html.tasks import generate_static_list_search_html
#         generate_static_list_search_html.delay()


admin.site.register(models.GoodsCategory) # , GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)