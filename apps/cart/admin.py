from django.contrib import admin
from django.db.models import Sum, F, DecimalField
from django.utils.html import format_html

from .models import Cart, CartItem


# ──────────────────────────────────────────────
#  1. Inline: عرض عناصر السلة داخل صفحة السلة
# ──────────────────────────────────────────────

class CartItemInline(admin.TabularInline):
    """
    عرض عناصر السلة (CartItem) كجدول مضمّن داخل صفحة تعديل السلة.
    الهدف: رؤية محتويات السلة بنظرة واحدة دون مغادرة الصفحة.
    """

    model = CartItem
    extra = 0  # عدم إظهار صفوف فارغة إضافية افتراضياً
    min_num = 0

    fields = (
        "id",
        "product",
        "service",
        "quantity",
        "price",
        "line_total_display",
        "added_at",
    )

    readonly_fields = (
        "id",
        "line_total_display",
        "added_at",
    )

    # ── تحسين الأداء: تحميل العلاقات مسبقاً ──
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("product", "service")
        )

    # ── عرض السعر الإجمالي للسطر ──
    @admin.display(description="إجمالي السطر")
    def line_total_display(self, obj):
        """عرض ناتج (السعر × الكمية) بتنسيق واضح."""
        if obj.pk:
            return f"{obj.line_total:,.2f}"
        return "-"


# ──────────────────────────────────────────────
#  2. CartAdmin: إدارة السلة الرئيسية
# ──────────────────────────────────────────────

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    واجهة إدارة سلة التسوق.
    تعرض ملخّصاً شاملاً: المالك، عدد العناصر، المجموع، والتواريخ.
    """

    # ── الأعمدة في صفحة القائمة ──
    list_display = (
        "id",
        "owner_display",
        "items_count_display",
        "total_price_display",
        "created_at",
        "updated_at",
    )

    list_display_links = ("id", "owner_display")

    # ── البحث والفلترة ──
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "session_key",
    )

    list_filter = (
        "created_at",
        "updated_at",
        ("user", admin.EmptyFieldListFilter),  # فلتر: مسجّل / زائر
    )

    # ── الحقول للقراءة فقط ──
    readonly_fields = (
        "total_price_display_detail",
        "items_count_display_detail",
        "created_at",
        "updated_at",
    )

    # ── تنظيم حقول صفحة التعديل ──
    fieldsets = (
        (
            "معلومات المالك",
            {
                "fields": ("user", "session_key"),
                "description": "السلة ترتبط إما بمستخدم مسجّل أو بجلسة زائر.",
            },
        ),
        (
            "ملخّص السلة",
            {
                "fields": (
                    "items_count_display_detail",
                    "total_price_display_detail",
                ),
            },
        ),
        (
            "التواريخ",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),  # قابلة للطي
            },
        ),
    )

    # ── العناصر المضمّنة ──
    inlines = [CartItemInline]

    # ── ترتيب افتراضي: الأحدث أولاً ──
    ordering = ("-updated_at",)

    # ── عدد العناصر في الصفحة ──
    list_per_page = 25

    # ════════════════════════════════════════════
    #  أعمدة مخصّصة لصفحة القائمة (list_display)
    # ════════════════════════════════════════════

    @admin.display(description="المالك", ordering="user__username")
    def owner_display(self, obj):
        """
        عرض اسم المالك:
        - المستخدم المسجّل → اسمه مع أيقونة 👤
        - الزائر → مفتاح الجلسة مختصراً مع أيقونة 🌐
        """
        if obj.user:
            name = obj.user.get_full_name() or obj.user.username
            return format_html(
                '<span title="مستخدم مسجّل">👤 {}</span>', name
            )
        if obj.session_key:
            return format_html(
                '<span title="{}" style="color:#888;">🌐 {}…</span>',
                obj.session_key,
                obj.session_key[:8],
            )
        return "-"

    @admin.display(description="عدد العناصر")
    def items_count_display(self, obj):
        """عدد العناصر — يُحسب من التعليق التوضيحي (annotation)."""
        count = getattr(obj, "_items_count", None)
        if count is None:
            count = obj.items_count  # fallback إلى الـ property
        return count

    @admin.display(description="المجموع الكلي")
    def total_price_display(self, obj):
        """المجموع الكلي — يُحسب من التعليق التوضيحي (annotation)."""
        total = getattr(obj, "_total_price", None)
        if total is None:
            total = obj.total_price  # fallback إلى الـ property
        if total:
            return f"{total:,.2f}"
        return "0.00"

    # ════════════════════════════════════════════
    #  حقول مخصّصة لصفحة التفاصيل (readonly_fields)
    # ════════════════════════════════════════════

    @admin.display(description="المجموع الكلي")
    def total_price_display_detail(self, obj):
        """عرض المجموع بخط كبير وواضح في صفحة التعديل."""
        if obj.pk:
            total = obj.total_price
            return format_html(
                '<span style="font-size:1.4em; font-weight:bold;'
                ' color:#27ae60;">{}</span>',
                f"{total:,.2f}",
            )
        return "-"

    @admin.display(description="عدد العناصر")
    def items_count_display_detail(self, obj):
        if obj.pk:
            return format_html(
                '<span style="font-size:1.2em;">{} عنصر</span>',
                obj.items_count,
            )
        return "-"

    # ════════════════════════════════════════════
    #  تحسين الأداء: تعليق توضيحي على مستوى الاستعلام
    # ════════════════════════════════════════════

    def get_queryset(self, request):
        """
        إضافة annotations لحساب عدد العناصر والمجموع الكلي
        على مستوى قاعدة البيانات — بدلاً من استعلام منفصل لكل سلة.
        هذا يحوّل N+1 queries إلى استعلام واحد.
        """
        qs = super().get_queryset(request)
        qs = qs.select_related("user")
        qs = qs.annotate(
            _items_count=Sum("items__quantity"),
            _total_price=Sum(
                F("items__price") * F("items__quantity"),
                output_field=DecimalField(),
            ),
        )
        return qs


# ──────────────────────────────────────────────
#  3. CartItemAdmin: إدارة منفصلة لعناصر السلات
# ──────────────────────────────────────────────

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    عرض منفصل لجميع عناصر السلات.
    مفيد لتحليل المنتجات/الخدمات الأكثر إضافة للسلات.
    """

    list_display = (
        "id",
        "cart_owner",
        "item_type_badge",
        "item_name_display",
        "quantity",
        "price",
        "line_total_display",
        "added_at",
    )

    list_display_links = ("id", "item_name_display")

    # ── الفلاتر ──
    list_filter = (
        "added_at",
        # فلتر مخصّص: نوع العنصر (منتج / خدمة)
        ("product", admin.EmptyFieldListFilter),
        ("service", admin.EmptyFieldListFilter),
    )

    search_fields = (
        "product__name",
        "service__name",
        "cart__user__username",
        "cart__session_key",
    )

    readonly_fields = ("added_at", "line_total_display")

    # ── تحسين الأداء ──
    list_select_related = ("cart", "cart__user", "product", "service")

    ordering = ("-added_at",)
    list_per_page = 30

    # ════════════════════════════════════════════
    #  أعمدة مخصّصة
    # ════════════════════════════════════════════

    @admin.display(description="مالك السلة", ordering="cart__user__username")
    def cart_owner(self, obj):
        """عرض مالك السلة التي ينتمي إليها العنصر."""
        cart = obj.cart
        if cart.user:
            return cart.user.get_full_name() or cart.user.username
        if cart.session_key:
            return f"زائر ({cart.session_key[:8]}…)"
        return "-"

    @admin.display(description="النوع")
    def item_type_badge(self, obj):
        """شارة ملوّنة توضّح نوع العنصر: منتج أو خدمة."""
        if obj.product:
            return format_html(
                '<span style="background:#3498db; color:#fff;'
                ' padding:2px 8px; border-radius:4px;'
                ' font-size:0.85em;">📦 منتج</span>'
            )
        if obj.service:
            return format_html(
                '<span style="background:#9b59b6; color:#fff;'
                ' padding:2px 8px; border-radius:4px;'
                ' font-size:0.85em;">🛠 خدمة</span>'
            )
        return "-"

    @admin.display(description="اسم العنصر")
    def item_name_display(self, obj):
        return obj.item_name

    @admin.display(description="إجمالي السطر")
    def line_total_display(self, obj):
        if obj.pk:
            return f"{obj.line_total:,.2f}"
        return "-"
