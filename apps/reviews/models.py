from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Review(models.Model):
    """
    نموذج التقييمات والمراجعات.

    يسمح للمستخدمين المسجّلين بتقييم المنتجات أو الخدمات
    بدرجة من 1 إلى 5 نجوم مع كتابة تعليق نصّي.

    القيود:
        - كل تقييم يرتبط إما بمنتج أو بخدمة (وليس كلاهما أو لا شيء).
        - المستخدم لا يمكنه تقييم نفس المنتج أو الخدمة أكثر من مرة.
    """

    # ══════════════════════════════════════════════════════════
    #                      العلاقات
    # ══════════════════════════════════════════════════════════

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='المستخدم',
    )

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='المنتج',
        null=True,
        blank=True,
    )

    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='الخدمة',
        null=True,
        blank=True,
    )

    # ══════════════════════════════════════════════════════════
    #                      المحتوى
    # ══════════════════════════════════════════════════════════

    rating = models.PositiveSmallIntegerField(
        verbose_name='التقييم',
        help_text='من 1 إلى 5 نجوم',
        validators=[
            MinValueValidator(1, message='أقل تقييم ممكن هو نجمة واحدة.'),
            MaxValueValidator(5, message='أعلى تقييم ممكن هو 5 نجوم.'),
        ],
    )

    comment = models.TextField(
        verbose_name='التعليق',
        help_text='اكتب مراجعتك هنا',
    )

    # ══════════════════════════════════════════════════════════
    #                      التواريخ
    # ══════════════════════════════════════════════════════════

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التعديل',
    )

    # ══════════════════════════════════════════════════════════
    #                 القيود على مستوى قاعدة البيانات
    # ══════════════════════════════════════════════════════════

    class Meta:
        verbose_name = 'تقييم'
        verbose_name_plural = 'التقييمات'
        ordering = ['-created_at']

        constraints = [
            # ──────────────────────────────────────────────
            # القيد 1: تقييم واحد لكل مستخدم لكل منتج
            # ──────────────────────────────────────────────
            # condition: فقط عندما يكون product مملوءاً
            # هذا يمنع المستخدم من تقييم نفس المنتج مرتين
            models.UniqueConstraint(
                fields=['user', 'product'],
                condition=models.Q(product__isnull=False),
                name='unique_user_product_review',
            ),

            # ──────────────────────────────────────────────
            # القيد 2: تقييم واحد لكل مستخدم لكل خدمة
            # ──────────────────────────────────────────────
            models.UniqueConstraint(
                fields=['user', 'service'],
                condition=models.Q(service__isnull=False),
                name='unique_user_service_review',
            ),

            # ──────────────────────────────────────────────
            # القيد 3: لا يمكن ربط التقييم بمنتج وخدمة معاً
            # ──────────────────────────────────────────────
            # إما product مملوء و service فارغ، أو العكس
            models.CheckConstraint(
                check=(
                    models.Q(
                        product__isnull=False,
                        service__isnull=True,
                    )
                    | models.Q(
                        product__isnull=True,
                        service__isnull=False,
                    )
                ),
                name='review_linked_to_product_xor_service',
            ),
        ]

    # ══════════════════════════════════════════════════════════
    #              التحقق على مستوى التطبيق (Django)
    # ══════════════════════════════════════════════════════════

    def clean(self):
        """
        تحقّق إضافي على مستوى Django (يعمل في Admin والـ Forms).

        القيد في Meta.constraints يحمي قاعدة البيانات مباشرة،
        لكن clean() يوفّر رسائل خطأ واضحة للمستخدم قبل
        الوصول لقاعدة البيانات.
        """
        super().clean()

        has_product = self.product_id is not None
        has_service = self.service_id is not None

        # ── الحالة 1: لم يُحدَّد منتج ولا خدمة ──
        if not has_product and not has_service:
            raise ValidationError(
                'يجب ربط التقييم بمنتج أو خدمة.',
                code='no_target',
            )

        # ── الحالة 2: تم تحديد منتج وخدمة معاً ──
        if has_product and has_service:
            raise ValidationError(
                'لا يمكن ربط التقييم بمنتج وخدمة في نفس الوقت.',
                code='dual_target',
            )

    # ══════════════════════════════════════════════════════════
    #                    التمثيل النصي
    # ══════════════════════════════════════════════════════════

    def __str__(self):
        # ── رمز النجمة لعرض مرئي ──
        stars = '★' * self.rating + '☆' * (5 - self.rating)

        # ── اسم الهدف (منتج أو خدمة) ──
        target = self.product or self.service or '—'

        return f'{self.user} → {target} | {stars}'

    # ══════════════════════════════════════════════════════════
    #                    خصائص مساعدة
    # ══════════════════════════════════════════════════════════

    @property
    def target_type(self):
        """نوع الهدف: product أو service."""
        if self.product_id:
            return 'product'
        return 'service'

    @property
    def target(self):
        """الكائن المُقيَّم (المنتج أو الخدمة)."""
        return self.product or self.service

    @property
    def stars_display(self):
        """تمثيل مرئي بالنجوم."""
        return '★' * self.rating + '☆' * (5 - self.rating)