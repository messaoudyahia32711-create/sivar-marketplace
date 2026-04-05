import uuid
from pathlib import Path
from django.db import models
from django.conf import settings


def store_logo_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f'stores/{uuid.uuid4().hex}/logo{ext}'


def store_banner_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f'stores/{uuid.uuid4().hex}/banner{ext}'


class Store(models.Model):
    vendor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='store',
        verbose_name='التاجر'
    )
    name          = models.CharField(max_length=255, blank=True, verbose_name='اسم المتجر')
    description   = models.TextField(blank=True, verbose_name='وصف المتجر')

    # ── حقول جديدة ──────────────────────────────────────────────
    logo          = models.ImageField(upload_to=store_logo_path, null=True, blank=True, verbose_name='الشعار')
    banner        = models.ImageField(upload_to=store_banner_path, null=True, blank=True, verbose_name='بانر المتجر')
    phone         = models.CharField(max_length=15, blank=True, verbose_name='رقم الهاتف')
    wilaya        = models.ForeignKey(
                      'localization.Wilaya',
                      on_delete=models.SET_NULL,
                      null=True, blank=True,
                      verbose_name='الولاية'
                    )
    location_detail = models.CharField(max_length=255, blank=True, verbose_name='الموقع داخل الحرم')
    manager_name    = models.CharField(max_length=255, blank=True, verbose_name='اسم مدير الحاضنة')
    return_policy = models.TextField(blank=True, verbose_name='سياسة الإرجاع')
    is_verified   = models.BooleanField(default=False, verbose_name='متجر موثّق')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'متجر'
        verbose_name_plural = 'المتاجر'

    def __str__(self):
        return self.name or f'متجر {self.vendor.username}'

class OrganizationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض')
    ]
    name = models.CharField(max_length=255, verbose_name='اسم المؤسسة')
    sector = models.CharField(max_length=255, verbose_name='المجال')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='الحالة'
    )
    incubator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_requests',
        null=True,
        blank=True,
        verbose_name='الحاضنة'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الطلب')

    class Meta:
        verbose_name = 'طلب انضمام مؤسسة'
        verbose_name_plural = 'طلبات انضمام المؤسسات'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'نسبة مئوية %'),
        ('fixed', 'مبلغ ثابت د.ج')
    ]
    APPLIES_TO_CHOICES = [
        ('all', 'الكل'),
        ('products', 'المنتجات فقط'),
        ('services', 'الخدمات فقط')
    ]
    
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coupons',
        verbose_name='التاجر'
    )
    code = models.CharField(max_length=50, unique=True, verbose_name='رمز الكوبون')
    type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage', verbose_name='نوع الخصم')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='القيمة')
    min_order = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='الحد الأدنى للطلب')
    max_uses = models.PositiveIntegerField(default=100, verbose_name='الحد الأقصى للاستخدامات')
    used = models.PositiveIntegerField(default=0, verbose_name='مرات الاستخدام')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    expires_at = models.DateField(verbose_name='تاريخ الانتهاء')
    applies_to = models.CharField(max_length=20, choices=APPLIES_TO_CHOICES, default='all', verbose_name='يُطبق على')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'كوبون'
        verbose_name_plural = 'الكوبونات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} - {self.vendor.username}'
