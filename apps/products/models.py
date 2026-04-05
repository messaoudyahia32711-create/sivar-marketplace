"""
نماذج تطبيق المنتجات — نظام المتجر الإلكتروني (Amazon-like).

الهيكل:
    Category      → تصنيفات هرمية لامحدودة المستويات (Self-referential)
    Product       → المنتج الرئيسي بكامل بياناته
    ProductImage  → معرض صور إضافية لكل منتج (One-to-Many)
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# ══════════════════════════════════════════════════════════════════
# Helper Functions — مسارات ديناميكية لرفع الملفات
# ══════════════════════════════════════════════════════════════════

def category_image_upload_path(instance, filename):
    """
    ينشئ مسار حفظ صورة التصنيف.
    النتيجة: media/categories/electronics/cover.jpg
    """
    return f'categories/{instance.slug}/{filename}'


def product_main_image_upload_path(instance, filename):
    """
    ينشئ مسار حفظ الصورة الرئيسية للمنتج.
    النتيجة: media/products/iphone-15-pro/main.jpg
    """
    return f'products/{instance.slug}/{filename}'


def product_gallery_upload_path(instance, filename):
    """
    ينشئ مسار حفظ صور معرض المنتج (الصور الإضافية).
    النتيجة: media/products/iphone-15-pro/gallery/side-view.jpg
    """
    return f'products/{instance.product.slug}/gallery/{filename}'


# ══════════════════════════════════════════════════════════════════
# 1. Category Model — نموذج التصنيف الهرمي
# ══════════════════════════════════════════════════════════════════

class Category(models.Model):
    """
    نموذج التصنيف مع دعم التسلسل الهرمي اللامحدود.

    يعتمد على Self-referential ForeignKey لبناء شجرة مثل:
        الإلكترونيات (مستوى 0 — جذر)
        ├── الهواتف الذكية (مستوى 1)
        │   ├── آيفون (مستوى 2)
        │   └── سامسونج (مستوى 2)
        └── أجهزة الكمبيوتر (مستوى 1)
    """

    name = models.CharField(
        max_length=200,
        verbose_name='اسم التصنيف',
        help_text='مثال: الإلكترونيات، الملابس، الأثاث',
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        allow_unicode=True,
        verbose_name='الرابط المختصر (Slug)',
        help_text='يُستخدم في روابط URL — يُملأ تلقائياً من الاسم',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='وصف التصنيف',
    )
    image = models.ImageField(
        upload_to=category_image_upload_path,
        blank=True,
        null=True,
        verbose_name='صورة التصنيف',
    )

    # ── Self-referential FK: الأب (None = تصنيف جذري) ─────────────
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',     # category.children.all() → التصنيفات الفرعية المباشرة
        verbose_name='التصنيف الأب',
        help_text='اتركه فارغاً إذا كان هذا تصنيفاً رئيسياً (جذراً)',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط',
        help_text='تعطيل التصنيف يُخفيه من الواجهة دون حذفه',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True,     verbose_name='آخر تحديث')

    class Meta:
        verbose_name        = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering            = ['name']
        indexes = [
            models.Index(fields=['slug'],      name='idx_cat_slug'),
            models.Index(fields=['parent'],    name='idx_cat_parent'),
            models.Index(fields=['is_active'], name='idx_cat_active'),
        ]

    def __str__(self):
        """يعرض المسار الكامل: الإلكترونيات › الهواتف › آيفون"""
        if self.parent:
            return f'{self.parent} › {self.name}'
        return self.name

    def save(self, *args, **kwargs):
        """ينشئ الـ Slug تلقائياً من الاسم إذا كان فارغاً."""
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    # Note: I'm commenting this out for now since URLs are not defined yet
    # def get_absolute_url(self):
    #     """يُرجع رابط صفحة التصنيف."""
    #     return reverse('products:category-detail', kwargs={'slug': self.slug})

    # ── Properties ─────────────────────────────────────────────────

    @property
    def is_root(self):
        """يُرجع True إذا كان التصنيف جذرياً (لا أب له)."""
        return self.parent is None

    @property
    def level(self):
        """
        يحسب مستوى التصنيف في الشجرة.
        الجذر = 0، أبناؤه = 1، أحفاده = 2 ...
        """
        depth   = 0
        current = self
        while current.parent is not None:
            depth  += 1
            current = current.parent
        return depth

    def get_ancestors(self):
        """
        يُرجع قائمة بكل أسلاف التصنيف مرتبةً من الجذر للأب المباشر.

        مثال: لتصنيف "آيفون" → [الإلكترونيات، الهواتف الذكية]
        """
        ancestors = []
        current   = self.parent
        while current is not None:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_all_children(self):
        """
        يُرجع كل التصنيفات الفرعية النشطة بشكل تكراري (عميق).

        مثال: للإلكترونيات → [الهواتف، آيفون، سامسونج، الكمبيوتر ...]
        تحذير: قد تُسبب مشكلة N+1 في الشجرات الكبيرة، استخدم django-mptt للحل.
        """
        result = list(self.children.filter(is_active=True))
        for child in self.children.filter(is_active=True):
            result.extend(child.get_all_children())
        return result


# ══════════════════════════════════════════════════════════════════
# 2. Custom Manager — مدير مخصص للمنتجات النشطة
# ══════════════════════════════════════════════════════════════════

class ActiveProductManager(models.Manager):
    """
    مدير مخصص يُرجع المنتجات المنشورة فقط (is_active=True).

    الاستخدام:
        Product.active.all()               → كل المنتجات النشطة
        Product.active.in_stock()          → النشطة والمتوفرة في المخزن
        Product.active.on_sale()           → النشطة التي عليها خصم
        Product.active.by_seller(user)     → منتجات بائع محدد
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def in_stock(self):
        """المنتجات النشطة والمتوفرة في المخزن (stock > 0)."""
        return self.get_queryset().filter(stock__gt=0)

    def on_sale(self):
        """المنتجات النشطة التي تملك سعر تخفيض."""
        return self.get_queryset().filter(discount_price__isnull=False)

    def featured(self):
        """المنتجات المميزة (للصفحة الرئيسية)."""
        return self.get_queryset().filter(is_featured=True)

    def by_vendor(self, vendor):
        """منتجات بائع محدد."""
        return self.get_queryset().filter(vendor=vendor)

    def by_category(self, category):
        """منتجات تصنيف محدد."""
        return self.get_queryset().filter(category=category)


# ══════════════════════════════════════════════════════════════════
# 3. Product Model — نموذج المنتج الرئيسي
# ══════════════════════════════════════════════════════════════════

class Product(models.Model):
    """
    النموذج المحوري للمنتج في المتجر الإلكتروني.

    يربط البائع (AUTH_USER_MODEL) بالتصنيف (Category) ويخزن
    كل البيانات: معلومات أساسية، تسعير، مخزون، صور، وحالة نشر.
    """

    # ── العلاقات (Relations) ────────────────────────────────────────

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',     # user.products.all() → كل منتجات البائع
        verbose_name='التاجر',
        help_text='المستخدم المالك لهذا المنتج',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,   # حذف التصنيف لا يحذف المنتج
        null=True,
        blank=True,
        related_name='products',     # category.products.all()
        verbose_name='التصنيف',
    )

    # ── المعلومات الأساسية (Basic Info) ────────────────────────────

    name = models.CharField(
        max_length=300,
        verbose_name='اسم المنتج',
        help_text='أدخل اسماً وصفياً ودقيقاً — يظهر في العناوين والبحث',
    )
    slug = models.SlugField(
        max_length=320,
        unique=True,
        allow_unicode=True,
        blank=True, # Added this to allow empty initial save
        verbose_name='الرابط المختصر (Slug)',
        help_text='يُملأ تلقائياً — لا تغيره بعد النشر لتجنب كسر الروابط',
    )
    description = models.TextField(
        verbose_name='وصف المنتج',
        help_text='وصف تفصيلي: المواصفات، الاستخدامات، المميزات',
    )
    brand = models.CharField(
        max_length=150,
        blank=True,
        default='',
        verbose_name='العلامة التجارية',
        help_text='مثال: Apple, Samsung, Nike',
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='رمز التخزين (SKU)',
        help_text='Stock Keeping Unit — مُعرِّف فريد للمنتج في المستودع',
    )

    # ── التسعير (Pricing) ───────────────────────────────────────────

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='السعر الأصلي (د.ج)',
        help_text='السعر الكامل قبل الخصم',
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='سعر التخفيض (د.ج)',
        help_text='اتركه فارغاً إذا لم يكن هناك خصم — يجب أن يكون أقل من السعر الأصلي',
    )

    # ── المخزون (Inventory) ─────────────────────────────────────────

    stock = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(999_999)],
        verbose_name='الكمية في المخزن',
        help_text='0 = غير متوفر حالياً',
    )

    # ── الحالة (Status) ─────────────────────────────────────────────

    is_active = models.BooleanField(
        default=True,
        verbose_name='منشور',
        help_text='False = مخفي تماماً من العملاء حتى لو كان في المخزون',
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='منتج مميز ⭐',
        help_text='يظهر في واجهة الصفحة الرئيسية والعروض المميزة',
    )

    # ── الصور (Images) ──────────────────────────────────────────────

    image_main = models.ImageField(
        upload_to=product_main_image_upload_path,
        blank=True,
        null=True,
        verbose_name='الصورة الرئيسية',
        help_text='تظهر في بطاقة المنتج وقوائم البحث — يُفضَّل 800×800 px',
    )

    # ── التواريخ (Timestamps) ───────────────────────────────────────

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإضافة',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخر تحديث',
    )

    # ── Managers ────────────────────────────────────────────────────

    objects = models.Manager()        # الافتراضي: يُرجع كل المنتجات (للـ Admin)
    active  = ActiveProductManager()  # المخصص: يُرجع النشطة فقط (للواجهة)

    # ── Meta ────────────────────────────────────────────────────────

    class Meta:
        verbose_name        = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering            = ['-created_at']  # الأحدث إضافةً يظهر أولاً
        indexes = [
            models.Index(fields=['slug'],         name='idx_prod_slug'),
            models.Index(fields=['vendor'],       name='idx_prod_vendor'),
            models.Index(fields=['category'],     name='idx_prod_category'),
            models.Index(fields=['is_active'],    name='idx_prod_active'),
            models.Index(fields=['is_featured'],  name='idx_prod_featured'),
            models.Index(fields=['price'],        name='idx_prod_price'),
            models.Index(fields=['-created_at'],  name='idx_prod_created'),
            # Index مركب للفلترة الشائعة: المنتجات النشطة حسب التصنيف
            models.Index(
                fields=['is_active', 'category'],
                name='idx_prod_active_category',
            ),
        ]
        constraints = [
            # قاعدة عمل: سعر التخفيض يجب أن يكون أقل من السعر الأصلي دائماً
            models.CheckConstraint(
                condition=(
                    models.Q(discount_price__isnull=True) |
                    models.Q(discount_price__lt=models.F('price'))
                ),
                name='chk_discount_less_than_price',
            ),
            # قاعدة عمل: المخزون لا يقبل قيماً سالبة (PositiveIntegerField تكفي لكن للتوضيح)
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='chk_price_positive',
            ),
        ]

    # ── Magic Methods ───────────────────────────────────────────────

    def __str__(self):
        """يعرض اسم المنتج مع سعره النهائي بعد الخصم."""
        final = self.get_final_price()
        return f'{self.name} — {final:,.2f} د.ج'

    def __repr__(self):
        return (
            f'<Product id={self.pk} '
            f'slug="{self.slug}" '
            f'price={self.price} '
            f'stock={self.stock}>'
        )

    # ── دالة الحفظ (Save Override) ──────────────────────────────────

    def save(self, *args, **kwargs):
        """
        ينشئ الـ Slug تلقائياً عند الإنشاء الأول فقط.

        لماذا الإنشاء فقط؟
            تغيير الـ Slug بعد النشر يكسر الروابط المحفوظة
            في محركات البحث والمفضلة.
        """
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    # ── دوال منطق الأعمال (Business Logic) ─────────────────────────

    def get_final_price(self):
        """
        يُرجع السعر الفعلي الذي سيدفعه العميل.

        المنطق:
            إذا كان discount_price موجوداً → يُرجعه.
            وإلا → يُرجع price العادي.

        Returns:
            Decimal: السعر النهائي.

        مثال:
            product.price = 5000
            product.discount_price = 3500
            product.get_final_price() → Decimal('3500.00')
        """
        if self.discount_price is not None:
            return self.discount_price
        return self.price

    def get_discount_percentage(self):
        """
        يحسب نسبة الخصم كرقم صحيح من 0 إلى 100.

        Returns:
            int: نسبة الخصم (0 إذا لم يكن هناك خصم).

        مثال:
            price=5000, discount_price=4000 → 20 (أي خصم 20%)
        """
        if not self.discount_price:
            return 0
        savings = self.price - self.discount_price
        return int((savings / self.price) * 100)

    def get_savings_amount(self):
        """
        يحسب مقدار التوفير بالعملة.

        Returns:
            Decimal: الفرق بين السعر الأصلي وسعر التخفيض.

        مثال:
            price=5000, discount_price=3500 → Decimal('1500.00')
        """
        if not self.discount_price:
            return Decimal('0.00')
        return self.price - self.discount_price

    # Note: I'm commenting this out for now since URLs are not defined yet
    # def get_absolute_url(self):
    #     """يُرجع رابط صفحة تفاصيل المنتج."""
    #     return reverse('products:product-detail', kwargs={'slug': self.slug})

    def reduce_stock(self, quantity: int):
        """
        يُنقص المخزون بعد إتمام طلب شراء.

        Args:
            quantity (int): الكمية المطلوبة.

        Raises:
            ValueError: إذا كانت الكمية المطلوبة أكبر من المتوفرة.

        مثال:
            product.reduce_stock(3)  # ينقص 3 وحدات من المخزن
        """
        if quantity > self.stock:
            raise ValueError(
                f'الكمية المطلوبة ({quantity}) أكبر من المتوفرة ({self.stock})'
            )
        self.stock -= quantity
        self.save(update_fields=['stock', 'updated_at'])

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_on_sale(self):
        """True إذا كان المنتج عليه تخفيض (discount_price موجود)."""
        return self.discount_price is not None

    @property
    def is_in_stock(self):
        """True إذا كانت الكمية المتوفرة أكبر من صفر."""
        return self.stock > 0

    @property
    def stock_status(self):
        """
        وصف نصي لحالة المخزون يُستخدم في الواجهة.

        Returns:
            str: 'متوفر' | 'كميات محدودة (n قطعة)' | 'غير متوفر'
        """
        if self.stock == 0:
            return 'غير متوفر'
        if self.stock <= 10:
            return f'كميات محدودة — {self.stock} قطعة فقط!'
        return 'متوفر في المخزن'

    @property
    def main_image_url(self):
        """
        يُرجع رابط الصورة الرئيسية بأمان (لا يرفع Exception إذا كانت فارغة).

        Returns:
            str | None: رابط الصورة أو None.
        """
        if self.image_main:
            return self.image_main.url
        return None


# ══════════════════════════════════════════════════════════════════
# 4. ProductImage Model — معرض صور المنتج الإضافية
# ══════════════════════════════════════════════════════════════════

class ProductImage(models.Model):
    """
    صور إضافية للمنتج بعلاقة One-to-Many مع Product.

    كل منتج يمكنه امتلاك عدد غير محدود من الصور الإضافية
    تُعرض في معرض الصور داخل صفحة المنتج.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',       # product.images.all() → كل الصور الإضافية
        verbose_name='المنتج',
    )
    image = models.ImageField(
        upload_to=product_gallery_upload_path,
        verbose_name='الصورة',
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='النص البديل (Alt)',
        help_text='مهم لـ SEO وإمكانية الوصول للمكفوفين',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='الترتيب',
        help_text='الرقم الأصغر يظهر أولاً في المعرض',
    )

    class Meta:
        verbose_name        = 'صورة المنتج'
        verbose_name_plural = 'صور المنتجات'
        ordering            = ['order', 'id']

    def __str__(self):
        return f'صورة [{self.order}] — {self.product.name}'