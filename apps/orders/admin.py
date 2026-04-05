from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


# ══════════════════════════════════════════════
# 1) عناصر الطلب كجدول مضمّن - OrderItemInline
# ══════════════════════════════════════════════

class OrderItemInline(admin.TabularInline):
    """
    عرض عناصر الطلب (منتجات / خدمات) داخل صفحة الطلب مباشرة.
    جميع الحقول للقراءة فقط لأن الطلبات المكتملة لا تُعدَّل.
    """
    model = OrderItem
    fields = ('product', 'service', 'price', 'quantity', 'item_subtotal')
    readonly_fields = ('product', 'service', 'price', 'quantity', 'item_subtotal')

    # لا نسمح بإضافة أو حذف عناصر من واجهة الإدارة
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        """منع إضافة عناصر جديدة من واجهة الإدارة."""
        return False

    @admin.display(description='المجموع الفرعي')
    def item_subtotal(self, obj):
        """عرض المجموع الفرعي لكل عنصر (السعر × الكمية)."""
        return f'{obj.subtotal:,.2f} د.ج'


# ══════════════════════════════════════════════
# 2) إدارة الطلبات - OrderAdmin
# ══════════════════════════════════════════════

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    واجهة إدارة شاملة للطلبات.
    مُنظّمة في أقسام واضحة مع إجراءات سريعة لتحديث الحالة.
    """

    # ──────────────────────────────────────────
    # إعدادات العرض في صفحة القائمة
    # ──────────────────────────────────────────

    list_display = (
        'id',
        'customer_name',
        'phone_number',
        'wilaya',
        'colored_status',
        'payment_method_display',
        'formatted_total',
        'is_paid_icon',
        'created_at',
    )

    list_display_links = ('id', 'customer_name')

    list_filter = (
        'status',
        'payment_method',
        'is_paid',
        'wilaya',
        ('created_at', admin.DateFieldListFilter),
    )

    search_fields = (
        'id',
        'first_name',
        'last_name',
        'phone_number',
        'email',
    )

    # ترتيب افتراضي: الأحدث أولاً
    ordering = ('-created_at',)

    # عدد الطلبات في الصفحة الواحدة
    list_per_page = 25

    # حقل التاريخ للتنقل السريع
    date_hierarchy = 'created_at'

    # ──────────────────────────────────────────
    # الحقول للقراءة فقط
    # ──────────────────────────────────────────

    readonly_fields = (
        'id',
        'total_price',
        'created_at',
        'updated_at',
    )

    # ──────────────────────────────────────────
    # تنظيم صفحة التفاصيل في أقسام (Fieldsets)
    # ──────────────────────────────────────────

    fieldsets = (
        ('معلومات الزبون', {
            'fields': (
                'user',
                ('first_name', 'last_name'),
                ('phone_number', 'email'),
            ),
        }),
        ('عنوان الشحن والتوصيل', {
            'fields': (
                ('wilaya', 'commune'),
                'address',
            ),
        }),
        ('معلومات الفاتورة والحالة', {
            'fields': (
                ('status', 'is_paid'),
                ('payment_method', 'total_price'),
            ),
        }),
        ('التواريخ', {
            'fields': (
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',),
        }),
    )

    # ──────────────────────────────────────────
    # الجدول المضمّن (Inline)
    # ──────────────────────────────────────────

    inlines = [OrderItemInline]

    # ──────────────────────────────────────────
    # أعمدة مخصّصة لصفحة القائمة
    # ──────────────────────────────────────────

    @admin.display(description='اسم الزبون', ordering='first_name')
    def customer_name(self, obj):
        """عرض الاسم الكامل للزبون."""
        return obj.get_full_name() or '—'

    @admin.display(description='المبلغ الإجمالي', ordering='total_price')
    def formatted_total(self, obj):
        """عرض المبلغ بتنسيق مقروء مع العملة."""
        return f'{obj.total_price:,.2f} د.ج'

    @admin.display(description='حالة الطلب', ordering='status')
    def colored_status(self, obj):
        """
        عرض حالة الطلب بألوان مميّزة لسهولة القراءة السريعة.
        أخضر = تم التوصيل، أحمر = ملغى، برتقالي = تم الشحن، إلخ.
        """
        colors = {
            Order.Status.PENDING:   '#f0ad4e',  # برتقالي
            Order.Status.CONFIRMED: '#5bc0de',  # أزرق فاتح
            Order.Status.SHIPPED:   '#0275d8',  # أزرق
            Order.Status.DELIVERED: '#5cb85c',  # أخضر
            Order.Status.CANCELLED: '#d9534f',  # أحمر
        }
        color = colors.get(obj.status, '#777')
        label = obj.get_status_display()

        return format_html(
            '<span style="'
            'background-color: {}; color: #fff; padding: 3px 10px;'
            'border-radius: 3px; font-size: 11px; font-weight: bold;'
            '">{}</span>',
            color,
            label,
        )

    @admin.display(description='طريقة الدفع', ordering='payment_method')
    def payment_method_display(self, obj):
        """عرض طريقة الدفع بنصّها العربي."""
        return obj.get_payment_method_display()

    @admin.display(description='الدفع', boolean=True, ordering='is_paid')
    def is_paid_icon(self, obj):
        """عرض حالة الدفع كأيقونة ✓ أو ✗."""
        return obj.is_paid

    # ──────────────────────────────────────────
    # إجراءات مخصّصة (Admin Actions)
    # ──────────────────────────────────────────

    actions = [
        'mark_as_confirmed',
        'mark_as_shipped',
        'mark_as_delivered',
        'mark_as_cancelled',
    ]

    @admin.action(description='✅ تأكيد الطلبات المحددة')
    def mark_as_confirmed(self, request, queryset):
        """تغيير حالة الطلبات المحددة إلى "مؤكّد"."""
        # نستثني الطلبات الملغاة والمُوصَّلة من التحديث
        eligible = queryset.filter(status=Order.Status.PENDING)
        updated = eligible.update(status=Order.Status.CONFIRMED)
        self.message_user(
            request,
            f'تم تأكيد {updated} طلب(ات) بنجاح.',
        )

    @admin.action(description='🚚 تحديد كـ "تم الشحن"')
    def mark_as_shipped(self, request, queryset):
        """تغيير حالة الطلبات المحددة إلى "تم الشحن"."""
        eligible = queryset.filter(status=Order.Status.CONFIRMED)
        updated = eligible.update(status=Order.Status.SHIPPED)
        self.message_user(
            request,
            f'تم تحديث {updated} طلب(ات) إلى "تم الشحن".',
        )

    @admin.action(description='📦 تحديد كـ "تم التوصيل"')
    def mark_as_delivered(self, request, queryset):
        """تغيير حالة الطلبات المحددة إلى "تم التوصيل"."""
        eligible = queryset.filter(status=Order.Status.SHIPPED)
        updated = eligible.update(
            status=Order.Status.DELIVERED,
            is_paid=True,  # عادةً يُدفع عند التوصيل (COD)
        )
        self.message_user(
            request,
            f'تم تحديث {updated} طلب(ات) إلى "تم التوصيل".',
        )

    @admin.action(description='❌ إلغاء الطلبات المحددة')
    def mark_as_cancelled(self, request, queryset):
        """إلغاء الطلبات التي لم تُشحن بعد."""
        # لا يمكن إلغاء طلب شُحن أو وُصّل
        non_cancellable = {Order.Status.SHIPPED, Order.Status.DELIVERED}
        eligible = queryset.exclude(status__in=non_cancellable)
        updated = eligible.update(status=Order.Status.CANCELLED)
        self.message_user(
            request,
            f'تم إلغاء {updated} طلب(ات).',
        )

    # ──────────────────────────────────────────
    # تحسينات الأداء
    # ──────────────────────────────────────────

    def get_queryset(self, request):
        """
        تحسين الاستعلام بجلب العلاقات المرتبطة مسبقاً
        لتقليل عدد الاستعلامات في صفحة القائمة.
        """
        return (
            super()
            .get_queryset(request)
            .select_related('user', 'wilaya', 'commune')
        )