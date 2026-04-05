from django.db import models
from django.conf import settings

class ServiceCategory(models.Model):
    """
    تصنيفات الخدمات (مثلاً: تصليح، تنظيف، تعليم).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم التصنيف")
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, verbose_name="الرابط اللطيف")

    class Meta:
        verbose_name = "تصنيف الخدمة"
        verbose_name_plural = "تصنيفات الخدمات"

    def __str__(self):
        return self.name


class Service(models.Model):
    """
    نموذج الخدمة (مثلاً: درس خصوصي، تصليح تكييف).
    """
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name="التاجر"
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='services',
        verbose_name="التصنيف"
    )
    
    name = models.CharField(max_length=200, verbose_name="اسم الخدمة")
    description = models.TextField(verbose_name="وصف الخدمة")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر (دج)")
    
    # التغطية الجغرافية: ربط بالولايات
    wilayas = models.ManyToManyField(
        'localization.Wilaya', 
        blank=True,
        verbose_name="مناطق التغطية (الولايات)"
    )
    
    image_main = models.ImageField(
        upload_to='services/images/', 
        blank=True, 
        null=True, 
        verbose_name="صورة الخدمة"
    )
    
    duration_hours = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        verbose_name="المدة التقريبية (بالساعات)"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "خدمة"
        verbose_name_plural = "الخدمات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.vendor.username}"


# ══════════════════════════════════════════════════════════════════
# 3. ServiceImage Model — معرض صور الخدمة الإضافية
# ══════════════════════════════════════════════════════════════════

class ServiceImage(models.Model):
    """
    صور إضافية للخدمة بعلاقة One-to-Many مع Service.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="الخدمة"
    )
    image = models.ImageField(
        upload_to='services/gallery/',
        verbose_name="الصورة"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="النص البديل (Alt)"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="الترتيب"
    )

    class Meta:
        verbose_name = "صورة الخدمة"
        verbose_name_plural = "صور الخدمات"
        ordering = ['order', 'id']

    def __str__(self):
        return f"صورة [{self.order}] — {self.service.name}"