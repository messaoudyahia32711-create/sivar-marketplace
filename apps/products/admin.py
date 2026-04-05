"""
تخصيص لوحة تحكم Django Admin لتطبيق المنتجات.

الملف: apps/products/admin.py

المحتويات:
    ProductImageInline  → معرض صور المنتج مضمَّن داخل صفحة التعديل
    CategoryAdmin       → إدارة التصنيفات الهرمية
    ProductAdmin        → إدارة المنتجات بكامل الميزات
"""

from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category, Product, ProductImage


# ══════════════════════════════════════════════════════════════════
# Inline Admin — صور المنتج الإضافية (معرض الصور)
# ══════════════════════════════════════════════════════════════════

class ProductImageInline(admin.TabularInline):
    """
    يُضمِّن صور المنتج الإضافية مباشرةً داخل صفحة تعديل المنتج.

    TabularInline  → عرض أفقي مضغوط (صفوف وأعمدة) مناسب للصور.
    StackedInline  → البديل: عرض رأسي موسَّع لكل سجل.
    """
    model           = ProductImage
    extra           = 3                         # 3 حقول رفع فارغة افتراضياً
    fields          = ['image', 'alt_text', 'order', 'thumbnail_preview']
    readonly_fields = ['thumbnail_preview']     # المعاينة للقراءة فقط (محسوبة)
    ordering        = ['order']

    @admin.display(description='معاينة')
    def thumbnail_preview(self, obj):
        """يعرض صورة مصغرة (80×80 px) للصورة المرفوعة مع تأثير بصري."""
        if obj.image:
            return format_html(
                '<img src="{url}" width="80" height="80" '
                'style="object-fit:cover; border-radius:6px; '
                'border:1px solid #dee2e6; '
                'box-shadow:0 1px 4px rgba(0,0,0,.12);">',
                url=obj.image.url,
            )
        return format_html(
            '<span style="color:#adb5bd; font-style:italic;">لم يُرفع بعد</span>'
        )


# ══════════════════════════════════════════════════════════════════
# CategoryAdmin — إدارة التصنيفات الهرمية
# ══════════════════════════════════════════════════════════════════

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    لوحة إدارة التصنيفات مع دعم كامل للهرمية متعددة المستويات.

    ملاحظة هامة:
        يجب تعريف search_fields هنا لأن ProductAdmin يستخدم
        autocomplete_fields = ['category']، وهذه الخاصية تعتمد
        على وجود search_fields في Admin النموذج المرتبط.
    """

    # ── قائمة العرض الرئيسية ────────────────────────────────────────
    list_display        = ['name', 'slug', 'parent', 'is_active', 'level_badge', 'products_count']
    list_display_links  = ['name', 'slug']          # الأعمدة القابلة للنقر
    list_editable       = ['is_active']             # تعديل الحالة مباشرةً من القائمة
    list_per_page       = 30
    list_select_related = ['parent']                # تجنب N+1 عند عرض عمود 'parent'

    # ── البحث والفلاتر ──────────────────────────────────────────────
    # ⚠️ search_fields مطلوب لـ autocomplete_fields في ProductAdmin
    search_fields = ['name', 'slug']
    list_filter   = ['is_active', 'parent']

    # ── تعبئة Slug تلقائياً ──────────────────────────────────────────
    prepopulated_fields = {'slug': ('name',)}

    # ── تنظيم نموذج التعديل (Fieldsets) ────────────────────────────
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('📂 المعلومات الأساسية', {
            'fields': ('name', 'slug', 'parent', 'description', 'image'),
        }),
        ('⚙️ الحالة', {
            'fields': ('is_active',),
        }),
        ('📅 التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),       # مطوي افتراضياً (أقل إزعاجاً)
        }),
    )

    # ── تحسين الأداء ────────────────────────────────────────────────
    def get_queryset(self, request):
        """
        يُضيف حقل _products_count بـ Annotation لتجنب N+1 Query.

        بدون هذا: كل صف سيُشغِّل استعلاماً منفصلاً لعدّ المنتجات.
        معه: استعلام واحد يجلب العدد لجميع الصفوف مرة واحدة.
        """
        return (
            super()
            .get_queryset(request)
            .annotate(_products_count=Count('products', distinct=True))
        )

    # ── Columns المخصصة ─────────────────────────────────────────────

    @admin.display(description='المنتجات', ordering='_products_count')
    def products_count(self, obj):
        """يعرض عدد المنتجات المرتبطة مع إمكانية الترتيب بالنقر."""
        count = obj._products_count
        if count == 0:
            return format_html('<span style="color:#adb5bd;">—</span>')
        return format_html(
            '<strong style="color:#0d6efd;">{}</strong>',
            count,
        )

    @admin.display(description='المستوى')
    def level_badge(self, obj):
        """
        يعرض مستوى التصنيف في الشجرة كشارة ملونة.
        المستوى 0 (جذر) = أخضر، 1 = أزرق، 2 = برتقالي، 3+ = أحمر.
        """
        LEVEL_STYLES = {
            0: ('جذر',     '#198754'),
            1: ('مستوى 1', '#0d6efd'),
            2: ('مستوى 2', '#fd7e14'),
            3: ('مستوى 3', '#dc3545'),
        }
        level = obj.level
        label, color = LEVEL_STYLES.get(level, (f'مستوى {level}', '#6c757d'))

        return format_html(
            '<span style="background:{color}; color:#fff; '
            'padding:2px 10px; border-radius:12px; '
            'font-size:11px; font-weight:600; '
            'white-space:nowrap;">'
            '{label}'
            '</span>',
            color=color,
            label=label,
        )


# ══════════════════════════════════════════════════════════════════
# ProductAdmin — إدارة المنتجات (النموذج الرئيسي)
# ══════════════════════════════════════════════════════════════════

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    لوحة إدارة المنتجات بكامل الميزات:

    ✔ التعديل السريع من القائمة (list_editable)
    ✔ أداء عالٍ مع آلاف السجلات (autocomplete + raw_id + select_related)
    ✔ إجراءات جماعية (Bulk Actions)
    ✔ تنقل هرمي بالتاريخ (date_hierarchy)
    ✔ معاينة الصور ومعلومات التسعير الغنية
    """

    # ══════════════════════════════════════════════════════════════
    # List View — إعدادات صفحة القائمة
    # ══════════════════════════════════════════════════════════════

    list_display = [
        # ─ العمود الأول: رابط لصفحة التعديل ─
        'name',
        # ─ معلومات العلاقات ─
        'vendor',
        'category',
        # ─ التسعير: حقول فعلية (مطلوبة لـ list_editable) ─
        'price',
        'discount_price',
        # ─ المخزون: حقل فعلي (مطلوب لـ list_editable) ─
        'stock',
        # ─ الحالة: حقول فعلية (مطلوبة لـ list_editable) ─
        'is_active',
        'is_featured',
        # ─ التاريخ ─
        'created_at',
    ]

    #
    # ⚠️ قواعد list_editable الثلاث:
    #    1. الحقل يجب أن يكون في list_display.
    #    2. الحقل يجب ألا يكون في list_display_links.
    #    3. الحقل لا يمكن أن يكون أول عمود في list_display.
    #
    list_display_links = ['name']
    list_editable      = ['price', 'stock', 'is_active', 'is_featured']

    list_per_page  = 25
    date_hierarchy = 'created_at'   # شريط تنقل هرمي: سنة → شهر → يوم
    ordering       = ['-created_at']    # الأحدث أولاً
    save_on_top    = True               # زر الحفظ في أعلى النموذج أيضاً

    # ── الفلاتر الجانبية ────────────────────────────────────────────
    list_filter = [
        'is_active',
        'is_featured',
        'category',
        ('created_at', admin.DateFieldListFilter),  # فلتر التاريخ المدمج في Django
    ]

    # ── حقول البحث ──────────────────────────────────────────────────
    search_fields = [
        'name',             # اسم المنتج
        'description',      # الوصف
        'sku',              # رمز التخزين
        'brand',            # العلامة التجارية
        'vendor__username', # اسم مستخدم البائع (Lookup عبر ForeignKey)
        'vendor__email',    # إيميل البائع
    ]

    # ══════════════════════════════════════════════════════════════
    # تحسين الأداء — بديل القوائم المنسدلة الضخمة
    # ══════════════════════════════════════════════════════════════

    #
    # autocomplete_fields → حقل بحث AJAX (تجربة مستخدم أفضل)
    # ─────────────────────────────────────────────────────────────
    # ✅ يتطلب: CategoryAdmin يجب أن يُعرِّف search_fields (وهو كذلك).
    # ✅ مثالي لـ category لأن عدد التصنيفات محدود نسبياً.
    # ✅ يعرض اسم التصنيف بشكل واضح في حقل البحث.
    #
    autocomplete_fields = ['category']

    #
    # raw_id_fields → حقل ID مع زر Popup للبحث (أكثر أماناً)
    # ─────────────────────────────────────────────────────────────
    # ✅ لا يعتمد على search_fields في Admin النموذج المرتبط.
    # ✅ مثالي لـ seller (AUTH_USER_MODEL) لأن:
    #    - عدد المستخدمين قد يصل لملايين.
    #    - النماذج المخصصة لـ User قد لا تُعرِّف search_fields.
    #    - يُظهر popup بحث بدلاً من قائمة منسدلة ضخمة.
    #
    raw_id_fields = ['vendor']

    # ── تعبئة Slug تلقائياً من Name (JavaScript) ─────────────────
    prepopulated_fields = {'slug': ('name',)}

    # ── الحقول للقراءة فقط ──────────────────────────────────────────
    readonly_fields = [
        'created_at',
        'updated_at',
        'main_image_preview',   # معاينة الصورة الرئيسية
        'pricing_summary',      # ملخص التسعير المحسوب
    ]

    # ══════════════════════════════════════════════════════════════
    # نموذج التعديل — Fieldsets منظَّمة
    # ══════════════════════════════════════════════════════════════

    fieldsets = (
        ('📦 المعلومات الأساسية', {
            'fields': (
                ('name', 'slug'),
                ('vendor', 'category'),
                ('brand',  'sku'),
            ),
        }),
        ('📝 وصف المنتج', {
            'fields': ('description',),
        }),
        ('💰 التسعير', {
            'fields': (
                ('price', 'discount_price'),
                'pricing_summary',              # ملخص احترافي (readonly)
            ),
            'description': (
                '⚠️ سعر الخصم اختياري — '
                'يجب أن يكون أقل تماماً من السعر الأصلي.'
            ),
        }),
        ('📊 المخزون', {
            'fields': ('stock',),
        }),
        ('🖼️ الصورة الرئيسية', {
            'fields': (
                'image_main',
                'main_image_preview',           # معاينة (readonly)
            ),
        }),
        ('⚙️ الإعدادات والحالة', {
            'fields': (
                ('is_active', 'is_featured'),
            ),
        }),
        ('📅 التواريخ (للقراءة فقط)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),           # مطوي افتراضياً
        }),
    )

    # ── صور المنتج الإضافية مضمَّنة ─────────────────────────────────
    inlines = [ProductImageInline]

    # ══════════════════════════════════════════════════════════════
    # تحسين الاستعلامات — select_related لتجنب N+1
    # ══════════════════════════════════════════════════════════════

    def get_queryset(self, request):
        """
        يُحمِّل seller و category مع Product في استعلام JOIN واحد.

        بدون select_related: كل صف في القائمة يُشغِّل استعلامَين
        إضافيَّين (للبائع وللتصنيف) → 25 صفحة * 2 = 50 استعلاماً!
        مع select_related: استعلام واحد فقط بـ JOIN.
        """
        return (
            super()
            .get_queryset(request)
            .select_related('vendor', 'category')
        )

    # ══════════════════════════════════════════════════════════════
    # Custom Display Methods — حقول العرض المخصصة (readonly)
    # ══════════════════════════════════════════════════════════════

    @admin.display(description='🖼️ معاينة الصورة الرئيسية')
    def main_image_preview(self, obj):
        """يعرض صورة مصغرة للمنتج (150×150 px) داخل نموذج التعديل."""
        if obj.image_main:
            return format_html(
                '<img src="{url}" width="150" height="150" '
                'style="object-fit:cover; border-radius:8px; '
                'border:1px solid #dee2e6; '
                'box-shadow:0 2px 8px rgba(0,0,0,.15);">',
                url=obj.image_main.url,
            )
        return format_html(
            '<span style="color:#adb5bd; font-style:italic;">'
            '📷 لم يتم رفع صورة رئيسية بعد.'
            '</span>'
        )

    @admin.display(description='📊 ملخص التسعير')
    def pricing_summary(self, obj):
        """
        يعرض ملخصاً احترافياً مقروءاً للتسعير يشمل:
        - السعر الأصلي (مشطوب عليه عند وجود خصم)
        - السعر النهائي بعد الخصم
        - نسبة التوفير ومبلغه

        يُستخدم داخل نموذج التعديل كحقل readonly.
        """
        # الكائن الجديد لم يُحفظ بعد → لا بيانات للعرض
        if not obj.pk:
            return format_html(
                '<span style="color:#adb5bd; font-style:italic;">'
                'احفظ المنتج أولاً لرؤية ملخص التسعير.'
                '</span>'
            )

        final   = obj.get_final_price()
        savings = obj.get_savings_amount()
        pct     = obj.get_discount_percentage()

        if obj.is_on_sale:
            return format_html(
                '<div style="font-family:monospace; line-height:2.2; font-size:13px;">'
                '📌 السعر الأصلي:&nbsp;'
                '<s style="color:#6c757d;">{price:,.2f} د.ج</s><br>'
                '🏷️ السعر النهائي:&nbsp;'
                '<strong style="color:#dc3545; font-size:1.15em;">{final:,.2f} د.ج</strong><br>'
                '💵 التوفير:&nbsp;'
                '<span style="color:#198754; font-weight:600;">'
                '{savings:,.2f} د.ج ({pct}% خصم)'
                '</span>'
                '</div>',
                price=obj.price,
                final=final,
                savings=savings,
                pct=pct,
            )

        return format_html(
            '<span style="font-family:monospace; font-size:14px; font-weight:600;">'
            '{price:,.2f} د.ج'
            '</span>'
            '&nbsp;<span style="color:#adb5bd; font-size:12px;">(لا يوجد خصم)</span>',
            price=final,
        )

    # ══════════════════════════════════════════════════════════════
    # Bulk Actions — إجراءات جماعية على المنتجات المحددة
    # ══════════════════════════════════════════════════════════════

    actions = [
        'action_activate',
        'action_deactivate',
        'action_mark_featured',
        'action_unmark_featured',
        'action_clear_discount',
    ]

    @admin.action(description='✅  تفعيل المنتجات المحددة')
    def action_activate(self, request, queryset):
        """يُغيِّر is_active=True لجميع المنتجات المحددة دفعةً واحدة."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'✅ تم تفعيل {updated} منتج بنجاح.',
            messages.SUCCESS,
        )

    @admin.action(description='🚫  إيقاف المنتجات المحددة')
    def action_deactivate(self, request, queryset):
        """يُغيِّر is_active=False لجميع المنتجات المحددة دفعةً واحدة."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'🚫 تم إيقاف {updated} منتج.',
            messages.WARNING,
        )

    @admin.action(description='⭐  تمييز المنتجات المحددة')
    def action_mark_featured(self, request, queryset):
        """يُغيِّر is_featured=True لجميع المنتجات المحددة."""
        updated = queryset.update(is_featured=True)
        self.message_user(
            request,
            f'⭐ تم تمييز {updated} منتج.',
            messages.SUCCESS,
        )

    @admin.action(description='☆  إلغاء تمييز المنتجات المحددة')
    def action_unmark_featured(self, request, queryset):
        """يُغيِّر is_featured=False لجميع المنتجات المحددة."""
        updated = queryset.update(is_featured=False)
        self.message_user(
            request,
            f'☆ تم إلغاء تمييز {updated} منتج.',
            messages.INFO,
        )

    @admin.action(description='🏷️  إزالة الخصم من المنتجات المحددة')
    def action_clear_discount(self, request, queryset):
        """يضبط discount_price=None للمنتجات التي تملك خصماً."""
        # نُصفِّي أولاً: فقط المنتجات التي لديها خصم فعلاً
        with_discount = queryset.exclude(discount_price__isnull=True)
        updated = with_discount.update(discount_price=None)

        if updated:
            self.message_user(
                request,
                f'🏷️ تم إزالة الخصم من {updated} منتج.',
                messages.INFO,
            )
        else:
            self.message_user(
                request,
                'لا توجد منتجات محددة تملك خصماً.',
                messages.WARNING,
            )