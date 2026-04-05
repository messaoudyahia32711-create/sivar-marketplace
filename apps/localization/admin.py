from django.contrib import admin
from .models import Wilaya, Commune

@admin.register(Wilaya)
class WilayaAdmin(admin.ModelAdmin):
    """
    إدارة الولايات في لوحة التحكم.
    """
    list_display = ['code', 'name', 'shipping_cost']
    list_editable = ['shipping_cost']  # يسمح بتعديل سعر التوصيل مباشرة من الجدول
    search_fields = ['name', 'code']
    ordering = ['code']

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    """
    إدارة البلديات في لوحة التحكم.
    """
    list_display = ['name', 'wilaya']
    list_filter = ['wilaya']  # فلترة البلديات حسب الولاية
    search_fields = ['name']
    # هذا يحسن الأداء عند تحميل قائمة البلديات (يجلب الولاية المرتبطة دفعة واحدة)
    list_select_related = ['wilaya'] 