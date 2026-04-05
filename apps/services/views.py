from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Service, ServiceCategory
from .serializers import ServiceSerializer, ServiceCategorySerializer


class IsVendorOrReadOnly(permissions.BasePermission):
    """
    صلاحية تسمح فقط لصاحب الخدمة أو المدير بتعديلها أو حذفها.
    الآخرون يمكنهم القراءة فقط.
    """
    def has_object_permission(self, request, view, obj):
        # السماح بعمليات القراءة للجميع
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # السماح بالكتابة للمالك أو للمدير (is_staff)
        return obj.vendor == request.user or request.user.is_staff


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة تصنيفات الخدمات.
    القراءة متاحة للجميع، التعديل والحذف للمدير فقط.
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    # تصحيح أمني: فقط المدير يمكنه إدارة التصنيفات
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة الخدمات.
    """
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsVendorOrReadOnly]
    
    # ربط الفلاتر والبحث
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'wilayas', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']
    pagination_class = None # Disable pagination for client-side catalog filtering

    def get_queryset(self):
        """
        تحسين الاستعلام وتصفية النتائج.
        """
        user = self.request.user
        
        # الاستعلام الأساسي مع تحسين الأداء (select_related & prefetch_related)
        # select_related: للحقول الأجنبية (vendor, category)
        # prefetch_related: للحقول المتعددة (wilayas)
        base_queryset = Service.objects.select_related('vendor', 'category').prefetch_related('wilayas')

        if user.is_authenticated:
            # المدير يرى كل شيء
            if user.is_staff:
                return base_queryset.all()
            # المستخدم العادي يرى خدماته (حتى غير النشطة) + الخدمات النشطة للآخرين
            return base_queryset.filter(Q(is_active=True) | Q(vendor=user)).distinct()
        
        # الزوار يرون فقط الخدمات النشطة
        return base_queryset.filter(is_active=True)

    def perform_create(self, serializer):
        """
        تعيين مقدم الخدمة تلقائياً عند الإنشاء.
        """
        serializer.save(vendor=self.request.user)