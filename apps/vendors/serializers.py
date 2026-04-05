from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.products.models import Product, ProductImage
from apps.services.models import Service, ServiceImage
from apps.reviews.models import Review
from apps.localization.models import Wilaya
from .models import Store


# ══════════════════════════════════════════════
# 1) Store
# ══════════════════════════════════════════════

class WilayaMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Wilaya
        fields = ['id', 'name']


class VendorStoreSerializer(serializers.ModelSerializer):
    wilaya = WilayaMinimalSerializer(read_only=True)
    wilaya_id = serializers.PrimaryKeyRelatedField(
        queryset=Wilaya.objects.all(),
        source='wilaya',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model  = Store
        fields = [
            'id', 'name', 'description', 'logo', 'banner',
            'phone', 'wilaya', 'wilaya_id', 'location_detail', 'manager_name',
            'return_policy', 'is_verified', 'created_at',
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']


# ══════════════════════════════════════════════
# 2) Dashboard Stats
# ══════════════════════════════════════════════

class TodayStatsSerializer(serializers.Serializer):
    orders       = serializers.IntegerField()
    revenue      = serializers.DecimalField(max_digits=14, decimal_places=2)
    new_customers = serializers.IntegerField()


class MonthStatsSerializer(serializers.Serializer):
    orders             = serializers.IntegerField()
    revenue            = serializers.DecimalField(max_digits=14, decimal_places=2)
    orders_change_pct  = serializers.FloatField()
    revenue_change_pct = serializers.FloatField()


class TotalStatsSerializer(serializers.Serializer):
    orders           = serializers.IntegerField()
    revenue          = serializers.DecimalField(max_digits=14, decimal_places=2)
    products         = serializers.IntegerField()
    services         = serializers.IntegerField()
    product_revenue  = serializers.DecimalField(max_digits=14, decimal_places=2)
    service_revenue  = serializers.DecimalField(max_digits=14, decimal_places=2)
    avg_rating       = serializers.FloatField(allow_null=True)


class VendorDashboardStatsSerializer(serializers.Serializer):
    store              = VendorStoreSerializer()
    today              = TodayStatsSerializer()
    this_month         = MonthStatsSerializer()
    total              = TotalStatsSerializer()
    pending_orders_count = serializers.IntegerField()
    low_stock_count    = serializers.IntegerField()


# ══════════════════════════════════════════════
# 3) Revenue Analytics
# ══════════════════════════════════════════════

class RevenueDataPointSerializer(serializers.Serializer):
    label        = serializers.CharField()
    revenue      = serializers.DecimalField(max_digits=14, decimal_places=2)
    orders_count = serializers.IntegerField()


class RevenueAnalyticsSerializer(serializers.Serializer):
    period = serializers.CharField()
    data   = RevenueDataPointSerializer(many=True)


# ══════════════════════════════════════════════
# 4) Orders
# ══════════════════════════════════════════════

class VendorOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', default=None)
    service_name = serializers.CharField(source='service.name', default=None)
    subtotal     = serializers.SerializerMethodField()

    class Meta:
        model  = OrderItem
        fields = ['id', 'product_name', 'service_name', 'price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.price * obj.quantity


class VendorOrderSerializer(serializers.ModelSerializer):
    # فقط عناصر هذا التاجر (تُمرَّر من الـ view عبر context)
    vendor_items     = serializers.SerializerMethodField()
    vendor_subtotal  = serializers.SerializerMethodField()
    customer_name    = serializers.SerializerMethodField()
    wilaya_name      = serializers.CharField(source='wilaya.name', read_only=True)
    commune_name     = serializers.CharField(source='commune.name', read_only=True)
    status_display   = serializers.CharField(source='get_status_display', read_only=True)
    payment_display  = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'customer_name', 'phone_number', 'email',
            'wilaya_name', 'commune_name', 'address',
            'status', 'status_display', 'payment_method', 'payment_display',
            'total_price', 'vendor_subtotal', 'vendor_items', 'created_at',
        ]

    def get_customer_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()

    def get_vendor_items(self, obj):
        vendor = self.context.get('vendor')
        # فقط عناصر هذا التاجر
        items = obj.items.filter(product__vendor=vendor).select_related('product', 'service')
        return VendorOrderItemSerializer(items, many=True).data

    def get_vendor_subtotal(self, obj):
        vendor = self.context.get('vendor')
        items = obj.items.filter(product__vendor=vendor)
        from django.db.models import Sum, F
        result = items.aggregate(
            subtotal=Sum(F('price') * F('quantity'))
        )['subtotal']
        return result or 0


class OrderStatusUpdateSerializer(serializers.Serializer):
    """
    التسلسل المسموح: pending → confirmed → shipped → delivered
    لا يُسمح بالرجوع أو القفز
    """
    STATUS_FLOW = {
        'pending':   'confirmed',
        'confirmed': 'shipped',
        'shipped':   'delivered',
    }
    new_status = serializers.ChoiceField(choices=Order.Status.choices)

    def validate_new_status(self, value):
        order = self.context['order']
        expected_next = self.STATUS_FLOW.get(order.status)
        if value != expected_next:
            raise serializers.ValidationError(
                f'الانتقال من "{order.get_status_display()}" إلى '
                f'"{Order.Status(value).label}" غير مسموح. '
                f'الحالة التالية المتوقعة: "{Order.Status(expected_next).label if expected_next else "لا شيء"}"'
            )
        return value


# ══════════════════════════════════════════════
# 5) Products
# ══════════════════════════════════════════════

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'order']

class VendorProductSerializer(serializers.ModelSerializer):
    """
    يتوقع هذا الـ serializer حقولاً مُضافة بـ annotate() في الـ view:
    - total_sold    : Sum('order_items__quantity')
    - total_revenue : Sum(F('order_items__price') * F('order_items__quantity'))
    - avg_rating    : Avg('reviews__rating')
    - reviews_count : Count('reviews', distinct=True)
    """
    category_name  = serializers.CharField(source='category.name', read_only=True)
    total_sold     = serializers.IntegerField(read_only=True, default=0)
    total_revenue  = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True, default=0)
    avg_rating     = serializers.FloatField(read_only=True, allow_null=True)
    reviews_count  = serializers.IntegerField(read_only=True, default=0)
    stock_status   = serializers.SerializerMethodField()
    images         = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'discount_price', 'stock',
            'stock_status', 'is_active', 'is_featured', 'category', 'category_name',
            'image_main', 'images', 'uploaded_images',
            'total_sold', 'total_revenue', 'avg_rating', 'reviews_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        for image_data in uploaded_images:
            ProductImage.objects.create(product=product, image=image_data)
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        instance = super().update(instance, validated_data)
        for image_data in uploaded_images:
            ProductImage.objects.create(product=instance, image=image_data)
        return instance

    def get_stock_status(self, obj):
        if obj.stock == 0:   return 'out'
        if obj.stock <= 5:   return 'critical'
        if obj.stock <= 10:  return 'low'
        return 'ok'


# ══════════════════════════════════════════════
# 6) Top Products
# ══════════════════════════════════════════════

class TopProductSerializer(serializers.Serializer):
    id           = serializers.IntegerField()
    name         = serializers.CharField()
    total_sold   = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    avg_rating   = serializers.FloatField(allow_null=True)


# ══════════════════════════════════════════════
# 7) Reviews
# ══════════════════════════════════════════════

class VendorReviewSerializer(serializers.ModelSerializer):
    product_name  = serializers.CharField(source='product.name', default=None)
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model  = Review
        fields = ['id', 'product_name', 'reviewer_name', 'rating', 'comment', 'created_at']

    def get_reviewer_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


# ══════════════════════════════════════════════
# 8) Coupons
# ══════════════════════════════════════════════

from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'type', 'value', 'min_order', 
            'max_uses', 'used', 'is_active', 'expires_at', 
            'applies_to', 'created_at'
        ]
        read_only_fields = ['id', 'used', 'created_at']

    def create(self, validated_data):
        vendor = self.context['request'].user
        validated_data['vendor'] = vendor
        return super().create(validated_data)


# ══════════════════════════════════════════════
# 9) Service Serializer (Aliased for Dashboard)
# ══════════════════════════════════════════════
from apps.services.serializers import ServiceSerializer as VendorServiceSerializer
