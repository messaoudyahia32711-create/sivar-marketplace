"""
روابط URL لتطبيق المنتجات.

الملف: apps/products/urls.py

الروابط المُولَّدة تلقائياً بواسطة DefaultRouter:
    /products/                     → GET (قائمة), POST (إضافة)
    /products/{id}/                → GET (تفاصيل), PUT (تعديل), DELETE (حذف)
    /products/my-products/         → GET (منتجات المستخدم الحالي)
    /products/{id}/toggle-active/  → POST (تفعيل/إلغاء تفعيل)
    /categories/                   → GET (قائمة التصنيفات)
    /categories/{id}/              → GET (تفاصيل تصنيف)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, CategoryViewSet

# إنشاء الراوتر الافتراضي
router = DefaultRouter()

# تسجيل واجهة المنتجات
router.register(r'products', ProductViewSet, basename='product')

# تسجيل واجهة التصنيفات
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]