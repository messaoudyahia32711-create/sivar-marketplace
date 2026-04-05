from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal


# ══════════════════════════════════════════════
# مُصادقات (Validators)
# ══════════════════════════════════════════════

phone_validator = RegexValidator(
    regex=r'^(0)(5|6|7)\d{8}$',
    message='أدخل رقم هاتف جزائري صالح (مثال: 0551234567).',
)


# ══════════════════════════════════════════════
# 1) نموذج الطلب الرئيسي - Order
# ══════════════════════════════════════════════

class Order(models.Model):
    """
    يمثّل طلب شراء واحد في المتجر.
    يدعم المستخدمين المسجّلين والزوار على حدّ سواء.
    يحتفظ بكامل بيانات الاتصال والعنوان والحالة المالية.
    """

    # ─── حالات الطلب ──────────────────────────
    class Status(models.TextChoices):
        PENDING   = 'pending',   'قيد الانتظار'
        CONFIRMED = 'confirmed', 'مؤكّد'
        SHIPPED   = 'shipped',   'تم الشحن'
        DELIVERED = 'delivered',  'تم التوصيل'
        CANCELLED = 'cancelled', 'ملغى'

    # ─── طرق الدفع ───────────────────────────
    class PaymentMethod(models.TextChoices):
        COD        = 'cod',        'الدفع عند الاستلام'
        CIB        = 'cib',        'بطاقة CIB'
        EDAHABIA   = 'edahabia',   'بطاقة الذهبية'

    # ──────────────────────────────────────────
    # الحقول الأساسية: معلومات صاحب الطلب
    # ──────────────────────────────────────────

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='المستخدم',
        help_text='يُترك فارغاً إذا كان الطلب من زائر.',
    )

    first_name = models.CharField(
        max_length=50,
        verbose_name='الاسم الأول',
    )

    last_name = models.CharField(
        max_length=50,
        verbose_name='اسم العائلة',
    )

    email = models.EmailField(
        verbose_name='البريد الإلكتروني',
        blank=True,
        default='',
    )

    phone_number = models.CharField(
        max_length=10,
        validators=[phone_validator],
        verbose_name='رقم الهاتف',
        help_text='رقم هاتف جزائري مكوّن من 10 أرقام.',
    )

    # ──────────────────────────────────────────
    # عنوان الشحن / التوصيل
    # ──────────────────────────────────────────

    wilaya = models.ForeignKey(
        'localization.Wilaya',
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='الولاية',
    )

    commune = models.ForeignKey(
        'localization.Commune',
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='البلدية',
    )

    address = models.TextField(
        verbose_name='العنوان بالتفصيل',
        help_text='رقم العمارة، الشارع، الحي... إلخ.',
    )

    # ──────────────────────────────────────────
    # المالية والحالة
    # ──────────────────────────────────────────

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='المبلغ الإجمالي',
        help_text='بالدينار الجزائري (DZD).',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='حالة الطلب',
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
        verbose_name='طريقة الدفع',
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name='تم الدفع؟',
    )

    # ──────────────────────────────────────────
    # التواريخ
    # ──────────────────────────────────────────

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ آخر تعديل',
    )

    # ──────────────────────────────────────────
    # Meta و __str__
    # ──────────────────────────────────────────

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        indexes = [
            models.Index(fields=['-created_at'], name='idx_order_created'),
            models.Index(fields=['status'], name='idx_order_status'),
            models.Index(fields=['user', 'status'], name='idx_order_user_status'),
        ]

    def __str__(self):
        owner = self.get_full_name() or f'زائر ({self.phone_number})'
        return f'طلب #{self.pk} — {owner}'

    # ──────────────────────────────────────────
    # دوال مساعدة
    # ──────────────────────────────────────────

    def get_full_name(self):
        """إرجاع الاسم الكامل لصاحب الطلب."""
        return f'{self.first_name} {self.last_name}'.strip()

    def calculate_total(self):
        """
        حساب المجموع الكلّي انطلاقاً من عناصر الطلب.
        لا يحفظ في قاعدة البيانات تلقائياً — استخدم update_total() للحفظ.
        """
        total = self.items.aggregate(
            total=models.Sum(
                models.F('price') * models.F('quantity'),
                output_field=models.DecimalField(),
            )
        )['total']

        return total or Decimal('0.00')

    def update_total(self):
        """حساب المجموع وحفظه مباشرة في قاعدة البيانات."""
        self.total_price = self.calculate_total()
        self.save(update_fields=['total_price', 'updated_at'])

    @classmethod
    def create_from_cart(cls, cart, **order_data):
        """
        إنشاء طلب كامل من سلة التسوق داخل عملية ذرّية (atomic).

        المعاملات:
            cart: كائن Cart يحتوي على العناصر المراد تحويلها.
            **order_data: بيانات الطلب (first_name, phone_number, wilaya...).

        المسار:
            1. إنشاء الطلب الرئيسي.
            2. تحويل كل عنصر في السلة إلى OrderItem مع لقطة السعر.
            3. إجراء حسم للمخزون (Stock Reduction) مع row-level lock.
            4. حساب المجموع الكلّي وحفظه.
            5. تفريغ السلة.

        يُرجع: كائن Order المُنشأ.
        """
        from apps.products.models import Product  # استيراد محلي لتجنب التعارض الدوري

        with transaction.atomic():
            # ── إنشاء الطلب ──
            order = cls.objects.create(**order_data)

            # ── تحويل عناصر السلة إلى عناصر طلب ──
            cart_items = cart.items.select_related('product', 'service').all()

            order_items = []
            for cart_item in cart_items:
                # تحديد السعر المعتمد وتقليل المخزون للمنتجات
                if cart_item.product:
                    # جلب المنتج مع قفل (Lock) لتجنب Race Condition
                    product = Product.objects.select_for_update().get(pk=cart_item.product_id)
                    
                    # خصم الكمية من المخزون (ستُطلق ValueError إذا لم يكفِ المخزون)
                    product.reduce_stock(cart_item.quantity)
                    
                    # استخدام السعر النهائي (بما في ذلك التخفيضات إن وجدت)
                    current_price = product.get_final_price()
                    
                elif cart_item.service:
                    # الخدمات لا تحتاج لإدارة مخزون
                    current_price = cart_item.service.price
                else:
                    continue

                order_items.append(
                    OrderItem(
                        order=order,
                        product=cart_item.product,
                        service=cart_item.service,
                        price=current_price,
                        quantity=cart_item.quantity,
                    )
                )

            # إدراج جماعي لعناصر الطلب
            OrderItem.objects.bulk_create(order_items)

            # ── حساب وحفظ المجموع ──
            order.update_total()

            # ── تفريغ السلة ──
            cart.items.all().delete()

        return order

    def cancel(self):
        """
        إلغاء الطلب بشكل آمن.
        لا يسمح بالإلغاء إذا كان الطلب قد شُحن أو وُصّل.
        """
        non_cancellable = {self.Status.SHIPPED, self.Status.DELIVERED}

        if self.status in non_cancellable:
            raise ValueError(
                f'لا يمكن إلغاء طلب بحالة "{self.get_status_display()}".'
            )

        self.status = self.Status.CANCELLED
        self.save(update_fields=['status', 'updated_at'])


# ══════════════════════════════════════════════
# 2) نموذج عنصر الطلب - OrderItem
# ══════════════════════════════════════════════

class OrderItem(models.Model):
    """
    يمثّل عنصراً واحداً داخل طلب.
    يحتفظ بلقطة (snapshot) من السعر وقت الشراء،
    بحيث لا تتأثر الفاتورة إذا تغيّر السعر لاحقاً.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='الطلب',
    )

    # ─── ربط بالمنتج أو الخدمة (أحدهما على الأقل) ───
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='المنتج',
    )

    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='الخدمة',
    )

    # ─── لقطة السعر والكمية ───
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='السعر عند الشراء',
        help_text='سعر الوحدة بالدينار الجزائري وقت إتمام الطلب.',
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='الكمية',
    )

    class Meta:
        verbose_name = 'عنصر طلب'
        verbose_name_plural = 'عناصر الطلب'
        constraints = [
            # ضمان أن العنصر مرتبط بمنتج أو خدمة (وليس كلاهما فارغ)
            models.CheckConstraint(
                check=(
                    models.Q(product__isnull=False)
                    | models.Q(service__isnull=False)
                ),
                name='orderitem_must_have_product_or_service',
            ),
        ]

    def __str__(self):
        item_name = self._get_item_name()
        return f'{item_name} × {self.quantity}'

    def _get_item_name(self):
        """إرجاع اسم المنتج أو الخدمة المرتبطة."""
        if self.product:
            return str(self.product)
        if self.service:
            return str(self.service)
        return 'عنصر محذوف'

    @property
    def subtotal(self):
        """حساب المجموع الفرعي لهذا العنصر (السعر × الكمية)."""
        return self.price * self.quantity