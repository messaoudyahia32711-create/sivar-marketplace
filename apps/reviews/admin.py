from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    واجهة إدارة التقييمات والمراجعات.

    تعرض التقييمات بطريقة مرئية واضحة مع نجوم ملونة
    وروابط مباشرة للمنتج أو الخدمة المُقيَّمة.
    """

    # ══════════════════════════════════════════════════════════
    #                   إعدادات العرض الرئيسية
    # ══════════════════════════════════════════════════════════

    list_display = (
        'user',
        'target_link',
        'colored_rating',
        'short_comment',
        'created_at',
    )

    list_filter = (
        'rating',
        ('created_at', admin.DateFieldListFilter),
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'product__name',
        'service__name',
        'comment',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)

    # ── عدد العناصر في الصفحة الواحدة ──
    list_per_page = 25

    # ══════════════════════════════════════════════════════════
    #                   تحسين الأداء
    # ══════════════════════════════════════════════════════════

    def get_queryset(self, request):
        """
        تحميل العلاقات مسبقاً لتفادي مشكلة N+1 Queries.

        بدون select_related:
            - عرض 25 تقييم = 1 + 25×3 = 76 استعلام ❌

        مع select_related:
            - عرض 25 تقييم = 1 استعلام واحد فقط ✅
        """
        return (
            super()
            .get_queryset(request)
            .select_related('user', 'product', 'service')
        )

    # ══════════════════════════════════════════════════════════
    #                 دوال العرض المخصصة
    # ══════════════════════════════════════════════════════════

    # ──────────────────────────────────────────────────────
    #  1) التقييم بنجوم ملونة
    # ──────────────────────────────────────────────────────

    @admin.display(description='التقييم', ordering='rating')
    def colored_rating(self, obj):
        """
        عرض التقييم كنجوم ملونة حسب الدرجة:

            ★★★★★  →  أخضر   (ممتاز)
            ★★★★☆  →  أخضر فاتح (جيد جداً)
            ★★★☆☆  →  برتقالي (متوسط)
            ★★☆☆☆  →  برتقالي غامق (ضعيف)
            ★☆☆☆☆  →  أحمر   (سيّئ)
        """
        # ── خريطة الألوان حسب عدد النجوم ──
        color_map = {
            5: '#2ecc71',   # أخضر — ممتاز
            4: '#27ae60',   # أخضر غامق — جيد جداً
            3: '#f39c12',   # برتقالي — متوسط
            2: '#e67e22',   # برتقالي غامق — ضعيف
            1: '#e74c3c',   # أحمر — سيّئ
        }

        color = color_map.get(obj.rating, '#95a5a6')

        # ── بناء النجوم الممتلئة والفارغة ──
        filled = '★' * obj.rating
        empty = '☆' * (5 - obj.rating)

        return format_html(
            '<span style="color: {}; font-size: 1.3em;"'
            ' title="{} من 5">{}{}</span>',
            color,
            obj.rating,
            filled,
            empty,
        )

    # ──────────────────────────────────────────────────────
    #  2) رابط المنتج أو الخدمة
    # ──────────────────────────────────────────────────────

    @admin.display(description='المنتج / الخدمة')
    def target_link(self, obj):
        """
        عرض اسم المنتج أو الخدمة كرابط قابل للنقر
        يؤدي مباشرة إلى صفحة تعديل ذلك الكائن في الأدمن.

        يُميَّز نوع الهدف بأيقونة:
            📦 للمنتجات
            🔧 للخدمات
        """
        if obj.product:
            # ── بناء رابط صفحة تعديل المنتج ──
            url = reverse(
                'admin:products_product_change',
                args=[obj.product.pk],
            )
            return format_html(
                '📦 <a href="{}" title="فتح صفحة المنتج"'
                ' style="font-weight:bold;">{}</a>',
                url,
                obj.product,
            )

        if obj.service:
            # ── بناء رابط صفحة تعديل الخدمة ──
            url = reverse(
                'admin:services_service_change',
                args=[obj.service.pk],
            )
            return format_html(
                '🔧 <a href="{}" title="فتح صفحة الخدمة"'
                ' style="font-weight:bold;">{}</a>',
                url,
                obj.service,
            )

        # ── حالة غير متوقعة: لا منتج ولا خدمة ──
        return format_html(
            '<span style="color:#e74c3c;">⚠️ غير مرتبط</span>'
        )

    # ──────────────────────────────────────────────────────
    #  3) اختصار التعليق
    # ──────────────────────────────────────────────────────

    @admin.display(description='التعليق')
    def short_comment(self, obj):
        """
        عرض أول 70 حرفاً من التعليق مع علامة «...»
        إن كان النص أطول من ذلك.

        هذا يمنع تمدّد الجدول أفقياً عند وجود تعليقات طويلة.
        """
        max_length = 70

        if len(obj.comment) <= max_length:
            return obj.comment

        return f'{obj.comment[:max_length]}...'

    # ══════════════════════════════════════════════════════════
    #                تنظيم صفحة التعديل (Fieldsets)
    # ══════════════════════════════════════════════════════════

    fieldsets = (
        (
            'الربط',
            {
                'fields': ('user', 'product', 'service'),
                'description': 'اربط التقييم بمنتج أو خدمة (وليس كلاهما).',
            },
        ),
        (
            'محتوى التقييم',
            {
                'fields': ('rating', 'comment'),
            },
        ),
        (
            'التواريخ',
            {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',),
            },
        ),
    )