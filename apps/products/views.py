from django.shortcuts import get_object_or_404, render
from django.db import models  # تم نقل الاستيراد للأعلى
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied  # تم نقل الاستيراد للأعلى
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Product, Category
from .serializers import (
    ProductSerializer, 
    ProductCreateUpdateSerializer, 
    CategorySerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet للأقسام - للقراءة فقط
    يوفر عمليات:
    - GET /categories/ (قائمة جميع الأقسام)
    - GET /categories/{id}/ (تفاصيل قسم محدد)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # متاح للجميع بدون تسجيل دخول


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet للمنتجات - عمليات CRUD كاملة
    يوفر عمليات:
    - GET /products/ (قائمة المنتجات مع فلترة وبحث)
    - POST /products/ (إنشاء منتج جديد - للبائعين المسجلين فقط)
    - GET /products/{id}/ (تفاصيل منتج محدد)
    - PUT/PATCH /products/{id}/ (تعديل منتج - للبائع المالك فقط)
    - DELETE /products/{id}/ (حذف منتج - للبائع المالك فقط)
    """
    
    # إعداد الفلترة والبحث
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']  # فلترة حسب القسم والحالة النشطة
    search_fields = ['name', 'description']  # البحث في الاسم والوصف
    ordering_fields = ['created_at', 'updated_at', 'name', 'price']
    ordering = ['-created_at']  # الترتيب الافتراضي حسب تاريخ الإنشاء (الأحدث أولاً)
    pagination_class = None # Disable pagination for client-side catalog filtering

    def get_permissions(self):
        """
        تخصيص الصلاحيات حسب نوع العملية
        """
        if self.action in ['list', 'retrieve']:
            # عمليات القراءة متاحة للجميع
            permission_classes = [AllowAny]
        else:
            # عمليات الكتابة تتطلب تسجيل الدخول
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        تخصيص السيريالايزر حسب نوع العملية
        """
        if self.action in ['create', 'update', 'partial_update']:
            # عمليات الإنشاء والتعديل تستخدم سيريالايزر مخصص
            return ProductCreateUpdateSerializer
        
        # باقي العمليات تستخدم السيريالايزر العادي
        return ProductSerializer

    def get_queryset(self):
        """
        تخصيص الاستعلام حسب نوع المستخدم
        """
        user = self.request.user
        
        # إذا كان المستخدم مدير أو موظف
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            # المدير يرى جميع المنتجات
            return Product.objects.all().select_related('category', 'vendor')
        
        # إذا كان المستخدم مسجل دخول وله دور البائع أو المؤسسة
        elif user.is_authenticated and hasattr(user, 'role') and user.role in ['SELLER', 'INSTITUTION']:
            # في قائمة المنتجات: يرى منتجاته + المنتجات النشطة للآخرين
            if self.action in ['list']:
                return Product.objects.filter(
                    models.Q(vendor=user) | models.Q(is_active=True)
                ).select_related('category', 'vendor')
            else:
                # في العمليات الأخرى: يرى منتجاته فقط
                return Product.objects.filter(vendor=user).select_related('category', 'vendor')
        
        # المستخدمون العاديون أو غير المسجلين يرون المنتجات النشطة فقط
        else:
            return Product.objects.filter(is_active=True).select_related('category', 'vendor')

    def perform_create(self, serializer):
        """
        تخصيص عملية الحفظ عند الإنشاء
        """
        user = self.request.user
        
        # التأكد من أن المستخدم له دور البائع (SELLER)
        if not hasattr(user, 'role') or user.role != 'SELLER':
            raise PermissionDenied("عذراً، يجب أن تملك حساب بائع (SELLER) لتتمكن من إضافة منتجات.")
        
        # حفظ المنتج مع تعيين البائع تلقائياً
        serializer.save(vendor=user)

    def perform_update(self, serializer):
        """
        تخصيص عملية التعديل - التأكد من أن المستخدم يعدل منتجه فقط
        """
        instance = self.get_object()
        user = self.request.user
        
        # التحقق من الملكية (إلا إذا كان مدير)
        if not (user.is_staff or user.is_superuser) and instance.vendor != user:
            raise PermissionDenied("لا يمكنك تعديل منتجات الآخرين")
        
        serializer.save()

    def perform_destroy(self, instance):
        """
        تخصيص عملية الحذف - التأكد من أن المستخدم يحذف منتجه فقط
        """
        user = self.request.user
        
        # التحقق من الملكية (إلا إذا كان مدير)
        if not (user.is_staff or user.is_superuser) and instance.vendor != user:
            raise PermissionDenied("لا يمكنك حذف منتجات الآخرين")
        
        instance.delete()

    @action(detail=False, methods=['get'], url_path='my-products')
    def my_products(self, request):
        """
        endpoint إضافي لعرض منتجات المستخدم الحالي فقط
        GET /products/my-products/
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "يجب تسجيل الدخول أولاً"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # استعلام منتجات المستخدم الحالي فقط
        queryset = Product.objects.filter(vendor=request.user).select_related('category')
        
        # تطبيق الفلترة والبحث
        queryset = self.filter_queryset(queryset)
        
        # تطبيق التصفح (pagination)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        """
        endpoint إضافي لتفعيل/إلغاء تفعيل منتج
        POST /products/{id}/toggle-active/
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "يجب تسجيل الدخول أولاً"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        product = self.get_object()
        
        # التحقق من الملكية (إلا إذا كان مدير)
        if not (request.user.is_staff or request.user.is_superuser) and product.vendor != request.user:
            return Response(
                {"detail": "لا يمكنك تعديل منتجات الآخرين"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # تبديل حالة التفعيل
        product.is_active = not product.is_active
        product.save()
        
        serializer = self.get_serializer(product)
        return Response({
            "message": f"تم {'تفعيل' if product.is_active else 'إلغاء تفعيل'} المنتج بنجاح",
            "product": serializer.data
        })

def home_view(request):
    """
    عرض الصفحة الرئيسية للمشروع.
    """
    return render(request, 'pages/index.html')

def catalog_view(request):
    """
    عرض صفحة المنتجات والخدمات (الكتالوج).
    """
    return render(request, 'pages/catalog.html')