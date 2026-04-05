from django.db import models

class Wilaya(models.Model):
    """
    نموذج الولاية الجزائرية (58 ولاية).
    يُستخدم لتحديد منطقة التوصيل ومنطقة تغطية الخدمات.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="اسم الولاية")
    code = models.IntegerField(unique=True, verbose_name="رمز الولاية")
    shipping_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="تكلفة التوصيل (دج)"
    )

    class Meta:
        verbose_name = "ولاية"
        verbose_name_plural = "الولايات"
        ordering = ['code'] # الترتيب حسب رقم الولاية

    def __str__(self):
        return f"{self.code} - {self.name}"


class Commune(models.Model):
    """
    نموذج البلدية التابعة لولاية معينة.
    """
    name = models.CharField(max_length=50, verbose_name="اسم البلدية")
    wilaya = models.ForeignKey(
        Wilaya, 
        on_delete=models.CASCADE, 
        related_name='communes',
        verbose_name="الولاية"
    )

    class Meta:
        verbose_name = "بلدية"
        verbose_name_plural = "البلديات"
        ordering = ['name'] # الترتيب حسب اسم البلدية

    def __str__(self):
        return f"{self.name} ({self.wilaya.name})"