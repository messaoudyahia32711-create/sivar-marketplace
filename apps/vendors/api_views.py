"""
API Views للوحة تحكم التاجر.
كل view يتحقق من: IsAuthenticated + role == SELLER
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Avg, Count, F, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin,
    CreateModelMixin, UpdateModelMixin, DestroyModelMixin
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action

from apps.orders.models import Order
from apps.products.models import Product
from apps.reviews.models import Review
from .models import Store
from apps.services.models import Service, ServiceImage, ServiceCategory
from .serializers import (
    VendorDashboardStatsSerializer,
    RevenueAnalyticsSerializer,
    VendorOrderSerializer,
    OrderStatusUpdateSerializer,
    VendorProductSerializer,
    VendorServiceSerializer,
    TopProductSerializer,
    VendorReviewSerializer,
    VendorStoreSerializer,
)


# ──────────────────────────────────────────────
# Permission مخصص للتجار فقط
# ──────────────────────────────────────────────

class IsSellerPermission(IsAuthenticated):
    """يسمح فقط للمستخدمين بدور SELLER أو INSTITUTION."""
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and hasattr(request.user, 'role')
            and request.user.role in ['SELLER', 'INSTITUTION']
        )


# ──────────────────────────────────────────────
# Pagination مخصص
# ──────────────────────────────────────────────

class VendorPagination(PageNumberPagination):
    page_size            = 20
    page_size_query_param = 'page_size'
    max_page_size        = 100


# ══════════════════════════════════════════════
# 1) Dashboard Overview
#    GET /api/vendors/dashboard/
# ══════════════════════════════════════════════

class DashboardOverviewAPIView(APIView):
    permission_classes = [IsSellerPermission]

    def get(self, request):
        user  = request.user
        today = timezone.now().date()

        # ── تحديد أول وآخر يوم في الشهر الحالي والماضي ──
        first_this_month = today.replace(day=1)
        first_last_month = (first_this_month - timedelta(days=1)).replace(day=1)
        last_last_month  = first_this_month - timedelta(days=1)

        # ── القاعدة: الطلبات التي تحتوي منتجات أو خدمات هذا التاجر ──
        vendor_orders = Order.objects.filter(
            Q(items__product__vendor=user) | Q(items__service__vendor=user)
        ).distinct()

        # ── إحصاءات اليوم ──
        today_orders = vendor_orders.filter(created_at__date=today)
        today_revenue = self._calc_revenue(today_orders, user)
        today_new_customers = today_orders.filter(
            user__isnull=False
        ).values('user').distinct().count()

        # ── إحصاءات هذا الشهر ──
        this_month_orders = vendor_orders.filter(
            created_at__date__gte=first_this_month
        )
        this_month_revenue = self._calc_revenue(this_month_orders, user)

        # ── إحصاءات الشهر الماضي (للمقارنة) ──
        last_month_orders = vendor_orders.filter(
            created_at__date__range=[first_last_month, last_last_month]
        )
        last_month_count   = last_month_orders.count()
        last_month_revenue = self._calc_revenue(last_month_orders, user)

        # ── حساب نسبة التغيير ──
        def pct_change(current, previous):
            if not previous:
                return 100.0 if current else 0.0
            return round((current - previous) / previous * 100, 1)

        this_month_count = this_month_orders.count()

        # ── الإجماليات ──
        total_orders  = vendor_orders.count()
        total_revenue = self._calc_revenue(vendor_orders, user)
        total_products = Product.objects.filter(vendor=user, is_active=True).count()
        total_services = Service.objects.filter(vendor=user, is_active=True).count()

        product_revenue = self._calc_revenue(vendor_orders, user, item_type='product')
        service_revenue = self._calc_revenue(vendor_orders, user, item_type='service')

        avg_rating = Review.objects.filter(
            product__vendor=user
        ).aggregate(avg=Avg('rating'))['avg']

        # ── تنبيهات ──
        pending_count  = vendor_orders.filter(status='pending').count()
        low_stock_count = Product.objects.filter(
            vendor=user, is_active=True, stock__lte=5
        ).count()

        # ── المتجر ──
        store, _ = Store.objects.select_related('wilaya').get_or_create(vendor=user)

        data = {
            'store': store,
            'today': {
                'orders':        today_orders.count(),
                'revenue':       today_revenue,
                'new_customers': today_new_customers,
            },
            'this_month': {
                'orders':             this_month_count,
                'revenue':            this_month_revenue,
                'orders_change_pct':  pct_change(this_month_count, last_month_count),
                'revenue_change_pct': pct_change(float(this_month_revenue), float(last_month_revenue)),
            },
            'total': {
                'orders':          total_orders,
                'revenue':         total_revenue,
                'products':        total_products,
                'services':        total_services,
                'product_revenue': product_revenue,
                'service_revenue': service_revenue,
                'avg_rating':      round(avg_rating, 2) if avg_rating else None,
            },
            'pending_orders_count': pending_count,
            'low_stock_count':      low_stock_count,
        }

        serializer = VendorDashboardStatsSerializer(data)
        return Response(serializer.data)

    @staticmethod
    def _calc_revenue(orders_qs, vendor, item_type=None):
        """حساب إجمالي إيراد التاجر من مجموعة طلبات (مع فلترة اختيارية للنوع)."""
        filters = Q(items__product__vendor=vendor) if item_type != 'service' else Q(items__service__vendor=vendor)
        
        if item_type == 'product':
            filters &= Q(items__product__isnull=False)
        elif item_type == 'service':
            filters &= Q(items__service__isnull=False)

        result = orders_qs.aggregate(
            revenue=Sum(
                F('items__price') * F('items__quantity'),
                filter=filters,
            )
        )['revenue']
        return result or Decimal('0.00')


# ══════════════════════════════════════════════
# 2) Revenue Analytics
#    GET /api/vendors/analytics/revenue/?period=7d|30d|12m
# ══════════════════════════════════════════════

class RevenueAnalyticsAPIView(APIView):
    permission_classes = [IsSellerPermission]

    def get(self, request):
        user   = request.user
        period = request.query_params.get('period', '30d')
        item_type = request.query_params.get('type', 'all') # 'product', 'service', or 'all'
        now    = timezone.now()

        if period == '7d':
            start    = now - timedelta(days=7)
            trunc_fn = TruncDay
            fmt      = '%Y-%m-%d'
        elif period == '12m':
            start    = now - timedelta(days=365)
            trunc_fn = TruncMonth
            fmt      = '%Y-%m'
        else:  # 30d default
            start    = now - timedelta(days=30)
            trunc_fn = TruncDay
            fmt      = '%Y-%m-%d'

        filters = Q(created_at__gte=start)
        if item_type == 'product':
            filters &= Q(items__product__vendor=user, items__product__isnull=False)
        elif item_type == 'service':
            filters &= Q(items__service__vendor=user, items__service__isnull=False)
        else:
            filters &= (Q(items__product__vendor=user) | Q(items__service__vendor=user))

        rows = (
            Order.objects
            .filter(filters)
            .distinct()
            .annotate(period=trunc_fn('created_at'))
            .values('period')
            .annotate(
                revenue=Sum(
                    F('items__price') * F('items__quantity'),
                    filter=(Q(items__product__vendor=user) if item_type != 'service' else Q(items__service__vendor=user)),
                ),
                orders_count=Count('id', distinct=True),
            )
            .order_by('period')
        )

        data = [
            {
                'label':        row['period'].strftime(fmt),
                'revenue':      row['revenue'] or Decimal('0.00'),
                'orders_count': row['orders_count'],
            }
            for row in rows
        ]

        return Response({'period': period, 'data': data})


# ══════════════════════════════════════════════
# 3) Orders Management
#    GET  /api/vendors/orders/
#    PATCH /api/vendors/orders/<id>/status/
# ══════════════════════════════════════════════

class VendorOrderListView(ListAPIView):
    permission_classes = [IsSellerPermission]
    serializer_class   = VendorOrderSerializer
    pagination_class   = VendorPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['status', 'payment_method']
    search_fields      = ['first_name', 'last_name', 'phone_number', 'id']
    ordering_fields    = ['created_at', 'total_price']
    ordering           = ['-created_at']

    def get_queryset(self):
        return (
            Order.objects
            .filter(items__product__vendor=self.request.user)
            .distinct()
            .select_related('wilaya', 'commune')
            .prefetch_related(
                'items__product',
                'items__service',
            )
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['vendor'] = self.request.user
        return ctx


class VendorOrderStatusUpdateView(APIView):
    permission_classes = [IsSellerPermission]

    def patch(self, request, pk):
        try:
            order = (
                Order.objects
                .filter(items__product__vendor=request.user)
                .distinct()
                .get(pk=pk)
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'الطلب غير موجود أو لا يخصّك.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrderStatusUpdateSerializer(
            data=request.data,
            context={'order': order},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order.status = serializer.validated_data['new_status']
        order.save(update_fields=['status', 'updated_at'])

        return Response({
            'order_id':   order.id,
            'new_status': order.status,
            'status_display': order.get_status_display(),
            'updated_at': order.updated_at,
        })


# ══════════════════════════════════════════════
# 4) Products CRUD
#    GET/POST /api/vendors/products/
#    GET/PUT/PATCH/DELETE /api/vendors/products/<id>/
#    PATCH /api/vendors/products/<id>/toggle-status/
# ══════════════════════════════════════════════

class VendorProductViewSet(
    ListModelMixin, RetrieveModelMixin, CreateModelMixin,
    UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    permission_classes = [IsSellerPermission]
    serializer_class   = VendorProductSerializer
    pagination_class   = VendorPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['is_active', 'category']
    search_fields      = ['name', 'description', 'sku']
    ordering_fields    = ['created_at', 'price', 'stock', 'total_sold']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = (
            Product.objects
            .filter(vendor=self.request.user)
            .select_related('category')
            .annotate(
                # الأسماء المؤكدة من الكود: order_items و reviews
                total_sold    = Sum('order_items__quantity'),
                total_revenue = Sum(
                    F('order_items__price') * F('order_items__quantity')
                ),
                avg_rating    = Avg('reviews__rating'),
                reviews_count = Count('reviews', distinct=True),
            )
        )
        # فلتر المخزون المنخفض
        if self.request.query_params.get('low_stock'):
            qs = qs.filter(stock__lte=5)
        return qs

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        product = self.get_object()
        product.is_active = not product.is_active
        product.save(update_fields=['is_active', 'updated_at'])
        return Response({
            'id':        product.id,
            'is_active': product.is_active,
            'message':   f'تم {"تفعيل" if product.is_active else "إيقاف"} المنتج بنجاح.',
        })

# ══════════════════════════════════════════════
# 4.1) Services CRUD
# ══════════════════════════════════════════════

class VendorServiceViewSet(
    ListModelMixin, RetrieveModelMixin, CreateModelMixin,
    UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    permission_classes = [IsSellerPermission]
    serializer_class   = VendorServiceSerializer
    pagination_class   = VendorPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['is_active', 'category']
    search_fields      = ['name', 'description']
    ordering_fields    = ['created_at', 'price']
    ordering           = ['-created_at']

    def get_queryset(self):
        return (
            Service.objects
            .filter(vendor=self.request.user)
            .select_related('category')
            .prefetch_related('images', 'wilayas')
        )

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        service = self.get_object()
        service.is_active = not service.is_active
        service.save(update_fields=['is_active', 'updated_at'])
        return Response({
            'id':        service.id,
            'is_active': service.is_active,
            'message':   f'تم {"تفعيل" if service.is_active else "إيقاف"} الخدمة بنجاح.',
        })


# ══════════════════════════════════════════════
# 4.2) Coupons CRUD
# ══════════════════════════════════════════════

from .models import Coupon
from .serializers import CouponSerializer

class CouponViewSet(
    ListModelMixin, RetrieveModelMixin, CreateModelMixin,
    UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    permission_classes = [IsSellerPermission]
    serializer_class   = CouponSerializer
    pagination_class   = VendorPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['is_active', 'type', 'applies_to']
    search_fields      = ['code']
    ordering_fields    = ['created_at', 'expires_at']
    ordering           = ['-created_at']

    def get_queryset(self):
        return Coupon.objects.filter(vendor=self.request.user)

    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        coupon = self.get_object()
        coupon.is_active = not coupon.is_active
        coupon.save(update_fields=['is_active'])
        return Response({
            'id':        coupon.id,
            'is_active': coupon.is_active,
            'message':   f'تم {"تفعيل" if coupon.is_active else "إيقاف"} الكوبون بنجاح.',
        })


# ══════════════════════════════════════════════
# 5) Top Products
#    GET /api/vendors/analytics/top-products/?limit=5&metric=revenue|quantity
# ══════════════════════════════════════════════

class VendorTopProductsAPIView(APIView):
    permission_classes = [IsSellerPermission]

    def get(self, request):
        metric = request.query_params.get('metric', 'revenue')
        limit  = min(int(request.query_params.get('limit', 5)), 20)

        qs = (
            Product.objects
            .filter(vendor=request.user)
            .annotate(
                total_sold    = Sum('order_items__quantity'),
                total_revenue = Sum(
                    F('order_items__price') * F('order_items__quantity')
                ),
                avg_rating    = Avg('reviews__rating'),
            )
        )

        order_by = '-total_revenue' if metric == 'revenue' else '-total_sold'
        qs = qs.order_by(order_by)[:limit]

        data = [
            {
                'id':            p.id,
                'name':          p.name,
                'total_sold':    p.total_sold or 0,
                'total_revenue': p.total_revenue or Decimal('0.00'),
                'avg_rating':    round(p.avg_rating, 2) if p.avg_rating else None,
            }
            for p in qs
        ]
        return Response({'metric': metric, 'results': data})


# ══════════════════════════════════════════════
# 6) Reviews
#    GET /api/vendors/reviews/?rating=&product_id=
# ══════════════════════════════════════════════

class VendorReviewListView(ListAPIView):
    permission_classes = [IsSellerPermission]
    serializer_class   = VendorReviewSerializer
    pagination_class   = VendorPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['rating', 'product']
    ordering_fields    = ['created_at', 'rating']
    ordering           = ['-created_at']

    def get_queryset(self):
        return (
            Review.objects
            .filter(product__vendor=self.request.user)
            .select_related('user', 'product')
        )


# ══════════════════════════════════════════════
# 7) Store Settings
#    GET /api/vendors/store/
#    PUT /api/vendors/store/
# ══════════════════════════════════════════════

class VendorStoreAPIView(APIView):
    permission_classes = [IsSellerPermission]

    def get(self, request):
        store, _ = Store.objects.select_related('wilaya').get_or_create(
            vendor=request.user
        )
        return Response(VendorStoreSerializer(store, context={'request': request}).data)

    def put(self, request):
        store, _ = Store.objects.get_or_create(vendor=request.user)
        serializer = VendorStoreSerializer(
            store,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


# ══════════════════════════════════════════════
# 8) Pending Orders Count (للـ Polling)
#    GET /api/vendors/orders/pending-count/
# ══════════════════════════════════════════════

class VendorPendingOrdersCountView(APIView):
    permission_classes = [IsSellerPermission]

    def get(self, request):
        count = (
            Order.objects
            .filter(items__product__vendor=request.user, status='pending')
            .distinct()
            .count()
        )
        return Response({'pending_count': count})


# ══════════════════════════════════════════════
# 9) Public Store Page (عامة - بدون مصادقة)
#    GET /api/vendors/public/store/<username>/
#    GET /api/vendors/public/store/<username>/products/
#    GET /api/vendors/public/store/<username>/services/
# ══════════════════════════════════════════════

from rest_framework.permissions import AllowAny
from apps.users.models import User


class PublicStoreAPIView(APIView):
    """واجهة المتجر العامة — متاحة لأي زائر دون تسجيل دخول."""
    permission_classes = [AllowAny]

    def get(self, request, username):
        try:
            vendor = User.objects.get(
                username=username,
                role__in=['VENDOR', 'INSTITUTION', 'SELLER']
            )
        except User.DoesNotExist:
            return Response({'error': 'المتجر غير موجود.'}, status=status.HTTP_404_NOT_FOUND)

        store, _ = Store.objects.select_related('wilaya').get_or_create(vendor=vendor)
        store_data = VendorStoreSerializer(store, context={'request': request}).data

        # Products
        products = (
            Product.objects
            .filter(vendor=vendor, is_active=True)
            .select_related('category')
            .prefetch_related('images')
            .annotate(
                avg_rating=Avg('reviews__rating'),
                total_sold=Sum('order_items__quantity'),
                total_revenue=Sum(F('order_items__price') * F('order_items__quantity')),
                reviews_count=Count('reviews', distinct=True),
            )
            .order_by('-created_at')[:50]
        )

        # Services
        services = (
            Service.objects
            .filter(vendor=vendor, is_active=True)
            .select_related('category')
            .prefetch_related('images', 'wilayas')
            .order_by('-created_at')[:50]
        )

        from .serializers import VendorProductSerializer, VendorServiceSerializer as SvcSerializer
        from apps.services.serializers import ServiceSerializer

        return Response({
            'store': store_data,
            'vendor': {
                'id': vendor.id,
                'username': vendor.username,
                'full_name': vendor.get_full_name(),
                'role': vendor.role,
                'is_verified': store.is_verified,
                'phone': store.phone,
            },
            'products': VendorProductSerializer(
                products, many=True, context={'request': request}
            ).data,
            'services': ServiceSerializer(
                services, many=True, context={'request': request}
            ).data,
        })


# ══════════════════════════════════════════════
# 10) Homepage API (عامة - الصفحة الرئيسية للسوق)
#     GET /api/vendors/api/public/homepage/
# ══════════════════════════════════════════════

from apps.products.models import Category
from apps.services.models import ServiceCategory as SvcCategory
from apps.localization.models import Wilaya


class HomepageAPIView(APIView):
    """
    واجهة الصفحة الرئيسية العامة — تُرجع كل البيانات اللازمة لعرض الصفحة الرئيسية.
    GET /api/vendors/api/public/homepage/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.products.serializers import CategorySerializer

        # ── 1) Product Categories ──
        product_categories = Category.objects.filter(is_active=True).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('-product_count')[:12]

        # ── 2) Service Categories ──
        service_categories = SvcCategory.objects.annotate(
            service_count=Count('services', filter=Q(services__is_active=True))
        ).order_by('-service_count')[:12]

        # ── 3) Featured Stores (Vendors) ──
        featured_stores = (
            Store.objects.filter(
                vendor__role__in=['VENDOR', 'SELLER'],
            )
            .select_related('vendor', 'wilaya')
            .annotate(
                products_count=Count(
                    'vendor__products',
                    filter=Q(vendor__products__is_active=True)
                ),
                avg_rating=Avg('vendor__products__reviews__rating'),
            )
            .order_by('-is_verified', '-products_count')[:6]
        )

        # ── 4) Featured Institutions ──
        featured_institutions = (
            Store.objects.filter(
                vendor__role='INSTITUTION',
            )
            .select_related('vendor', 'wilaya')
            .annotate(
                services_count=Count(
                    'vendor__services',
                    filter=Q(vendor__services__is_active=True)
                ),
                products_count=Count(
                    'vendor__products',
                    filter=Q(vendor__products__is_active=True)
                ),
            )
            .order_by('-is_verified', '-services_count')[:6]
        )

        # ── 5) Featured Products ──
        featured_products = (
            Product.objects
            .filter(is_active=True, is_featured=True)
            .select_related('category', 'vendor')
            .prefetch_related('images')
            .annotate(
                avg_rating=Avg('reviews__rating'),
                reviews_count=Count('reviews', distinct=True),
                total_sold=Sum('order_items__quantity'),
                total_revenue=Sum(F('order_items__price') * F('order_items__quantity')),
            )
            .order_by('-created_at')[:12]
        )

        # ── 6) Discounted Products ──
        discounted_products = (
            Product.objects
            .filter(is_active=True, discount_price__isnull=False)
            .select_related('category', 'vendor')
            .prefetch_related('images')
            .annotate(
                avg_rating=Avg('reviews__rating'),
                reviews_count=Count('reviews', distinct=True),
                total_sold=Sum('order_items__quantity'),
                total_revenue=Sum(F('order_items__price') * F('order_items__quantity')),
            )
            .order_by('-created_at')[:12]
        )

        # ── 7) Latest Products ──
        latest_products = (
            Product.objects
            .filter(is_active=True)
            .select_related('category', 'vendor')
            .prefetch_related('images')
            .annotate(
                avg_rating=Avg('reviews__rating'),
                reviews_count=Count('reviews', distinct=True),
                total_sold=Sum('order_items__quantity'),
                total_revenue=Sum(F('order_items__price') * F('order_items__quantity')),
            )
            .order_by('-created_at')[:12]
        )

        # ── 7.5) Services ──
        latest_services = (
            Service.objects
            .filter(is_active=True)
            .select_related('category', 'vendor')
            .prefetch_related('images', 'wilayas')
            .order_by('-created_at')[:12]
        )
        # We don't have is_featured on Services yet, so we'll just sort by some other metric or take top 12.
        featured_services = (
            Service.objects
            .filter(is_active=True)
            .select_related('category', 'vendor')
            .prefetch_related('images', 'wilayas')
            .annotate(wilayas_count=Count('wilayas'))
            .order_by('-wilayas_count', '-created_at')[:12]
        )

        # ── 8) Stats ──
        total_stores = Store.objects.filter(
            vendor__role__in=['VENDOR', 'SELLER']
        ).count()
        total_institutions = Store.objects.filter(
            vendor__role='INSTITUTION'
        ).count()
        total_products = Product.objects.filter(is_active=True).count()
        total_services = Service.objects.filter(is_active=True).count()
        total_wilayas = Wilaya.objects.count()

        # ── Build Response ──
        store_serializer_data = []
        for s in featured_stores:
            store_serializer_data.append({
                'id': s.id,
                'name': s.name or f"متجر {s.vendor.username}",
                'logo': request.build_absolute_uri(s.logo.url) if s.logo else None,
                'banner': request.build_absolute_uri(s.banner.url) if s.banner else None,
                'is_verified': s.is_verified,
                'wilaya_name': s.wilaya.name if s.wilaya else None,
                'username': s.vendor.username,
                'products_count': s.products_count,
                'avg_rating': round(s.avg_rating, 1) if s.avg_rating else None,
            })

        institution_data = []
        for s in featured_institutions:
            institution_data.append({
                'id': s.id,
                'name': s.name or f"مؤسسة {s.vendor.username}",
                'logo': request.build_absolute_uri(s.logo.url) if s.logo else None,
                'banner': request.build_absolute_uri(s.banner.url) if s.banner else None,
                'is_verified': s.is_verified,
                'wilaya_name': s.wilaya.name if s.wilaya else None,
                'username': s.vendor.username,
                'services_count': s.services_count,
                'products_count': s.products_count,
            })

        product_cat_data = []
        for c in product_categories:
            product_cat_data.append({
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'product_count': c.product_count,
            })

        service_cat_data = []
        for c in service_categories:
            service_cat_data.append({
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'service_count': c.service_count,
            })

        from apps.services.serializers import ServiceSerializer
        
        return Response({
            'product_categories': product_cat_data,
            'service_categories': service_cat_data,
            'featured_stores': store_serializer_data,
            'featured_institutions': institution_data,
            'featured_products': VendorProductSerializer(
                featured_products, many=True, context={'request': request}
            ).data,
            'discounted_products': VendorProductSerializer(
                discounted_products, many=True, context={'request': request}
            ).data,
            'latest_products': VendorProductSerializer(
                latest_products, many=True, context={'request': request}
            ).data,
            'featured_services': ServiceSerializer(
                featured_services, many=True, context={'request': request}
            ).data,
            'latest_services': ServiceSerializer(
                latest_services, many=True, context={'request': request}
            ).data,
            'stats': {
                'total_stores': total_stores,
                'total_institutions': total_institutions,
                'total_products': total_products,
                'total_services': total_services,
                'total_wilayas': total_wilayas,
            }
        })

