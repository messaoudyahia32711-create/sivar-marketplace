from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Cart(models.Model):
    """
    نموذج سلة التسوق.
    يدعم المستخدمين المسجّلين (عبر user) والزوار (عبر session_key).
    كل مستخدم مسجّل يملك سلة واحدة فقط (OneToOneField).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        null=True,
        blank=True,
        verbose_name="المستخدم",
        help_text="يُربط فقط إذا كان المستخدم مسجّلاً.",
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="مفتاح الجلسة",
        help_text="يُستخدم لربط السلة بالزائر غير المسجّل.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ آخر تعديل",
    )

    class Meta:
        verbose_name = "سلة تسوق"
        verbose_name_plural = "سلات التسوق"
        constraints = [
            # ضمان أن السلة مرتبطة إما بمستخدم أو بجلسة — وليس فارغة من كليهما
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, session_key__isnull=True)
                    | models.Q(user__isnull=True, session_key__isnull=False)
                ),
                name="cart_user_or_session_not_both",
                violation_error_message="السلة يجب أن ترتبط بمستخدم أو بجلسة، وليس كليهما أو لا شيء.",
            ),
        ]

    def __str__(self):
        if self.user:
            return f"سلة {self.user.get_full_name() or self.user.username}"
        return f"سلة زائر ({self.session_key[:8]}...)"

    @property
    def total_price(self):
        """
        حساب المجموع الكلي لجميع عناصر السلة.
        يعتمد على السعر المُخزَّن في CartItem (وقت الإضافة)
        وليس السعر الحالي للمنتج/الخدمة — لتجنب مشاكل تغيّر الأسعار.
        """
        total = self.items.aggregate(
            total=models.Sum(
                models.F("price") * models.F("quantity"),
                output_field=models.DecimalField(),
            )
        )["total"]
        return total or 0

    @property
    def items_count(self):
        """عدد العناصر الإجمالي في السلة (مع مراعاة الكميات)."""
        return self.items.aggregate(
            count=models.Sum("quantity")
        )["count"] or 0

    def clean(self):
        """التحقق على مستوى النموذج: مستخدم أو جلسة وليس كلاهما."""
        super().clean()
        has_user = self.user is not None
        has_session = bool(self.session_key)

        if has_user and has_session:
            raise ValidationError(
                "لا يمكن ربط السلة بمستخدم وجلسة في نفس الوقت."
            )
        if not has_user and not has_session:
            raise ValidationError(
                "يجب ربط السلة بمستخدم مسجّل أو بمفتاح جلسة زائر."
            )


class CartItem(models.Model):
    """
    عنصر داخل سلة التسوق.
    يمكن أن يكون إما منتجاً (Product) أو خدمة (Service) — وليس كليهما.
    السعر يُحفظ لحظة الإضافة (Snapshot) لضمان ثبات السعر
    حتى لو تغيّر سعر المنتج/الخدمة لاحقاً.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="السلة",
    )

    # ========== الربط بالمنتج أو الخدمة ==========

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True,
        blank=True,
        verbose_name="المنتج",
        help_text="يُملأ فقط إذا كان العنصر منتجاً.",
    )

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True,
        blank=True,
        verbose_name="الخدمة",
        help_text="يُملأ فقط إذا كان العنصر خدمة.",
    )

    # ========== بيانات العنصر ==========

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="الكمية",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="السعر عند الإضافة",
        help_text="سعر الوحدة لحظة إضافتها للسلة (Snapshot).",
    )

    added_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name="تاريخ الإضافة",
    )

    class Meta:
        verbose_name = "عنصر في السلة"
        verbose_name_plural = "عناصر السلة"
        constraints = [
            # ضمان أن العنصر إما منتج أو خدمة — وليس كلاهما أو لا شيء
            models.CheckConstraint(
                check=(
                    models.Q(product__isnull=False, service__isnull=True)
                    | models.Q(product__isnull=True, service__isnull=False)
                ),
                name="cartitem_product_or_service_not_both",
                violation_error_message="العنصر يجب أن يكون إما منتجاً أو خدمة.",
            ),
            # منع تكرار نفس المنتج في نفس السلة
            models.UniqueConstraint(
                fields=["cart", "product"],
                condition=models.Q(product__isnull=False),
                name="unique_product_per_cart",
            ),
            # منع تكرار نفس الخدمة في نفس السلة
            models.UniqueConstraint(
                fields=["cart", "service"],
                condition=models.Q(service__isnull=False),
                name="unique_service_per_cart",
            ),
        ]

    def __str__(self):
        item_name = self.item_name
        return f"{item_name} × {self.quantity}"

    @property
    def item_name(self):
        """اسم العنصر سواء كان منتجاً أو خدمة."""
        if self.product:
            return str(self.product)
        if self.service:
            return str(self.service)
        return "عنصر غير معروف"

    @property
    def line_total(self):
        """السعر الإجمالي لهذا السطر = سعر الوحدة × الكمية."""
        return self.price * self.quantity

    def clean(self):
        """
        التحقق من صحة البيانات:
        1. العنصر يجب أن يكون منتجاً أو خدمة (وليس كليهما أو لا شيء).
        2. الكمية يجب أن تكون 1 على الأقل.
        """
        super().clean()

        has_product = self.product is not None
        has_service = self.service is not None

        if has_product and has_service:
            raise ValidationError(
                "لا يمكن أن يكون العنصر منتجاً وخدمة في نفس الوقت."
            )
        if not has_product and not has_service:
            raise ValidationError(
                "يجب تحديد منتج أو خدمة لهذا العنصر."
            )

        if self.quantity is not None and self.quantity < 1:
            raise ValidationError({"quantity": "الكمية يجب أن تكون 1 على الأقل."})

    def save(self, *args, **kwargs):
        """
        عند الحفظ، نُحدِّث حقل updated_at في السلة الأم
        لتتبّع آخر نشاط على السلة.
        """
        self.full_clean()
        super().save(*args, **kwargs)
        # تحديث updated_at للسلة الأم
        Cart.objects.filter(pk=self.cart_id).update(
            updated_at=models.functions.Now()
        )