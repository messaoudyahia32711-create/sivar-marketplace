from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, ServiceCategoryViewSet

# إنشاء الراوتر الافتراضي
router = DefaultRouter()

# تسجيل واجهة الخدمات
# ينشئ روابط مثل: /services/, /services/{id}/
router.register(r'services', ServiceViewSet, basename='service')

# تسجيل واجهة تصنيفات الخدمات
# ينشئ روابط مثل: /categories/, /categories/{id}/
router.register(r'categories', ServiceCategoryViewSet, basename='service-category')

urlpatterns = [
    path('', include(router.urls)),
]