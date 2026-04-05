"""
ملف النماذج الخاص بتطبيق المستخدمين.
يحتوي على نموذج المستخدم المخصص لمنصة التجارة الإلكترونية الجزائرية.
"""
import uuid
from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# -----------------------------------------------------------------------
# دوال مساعدة - Helper Functions
# -----------------------------------------------------------------------

def user_profile_picture_path(instance, filename: str) -> str:
    """
    توليد مسار فريد لحفظ صورة الملف الشخصي.

    يستخدم UUID لتجنب التعارض بين أسماء الملفات وتعزيز الأمان
    بحيث لا يمكن تخمين مسارات الصور.

    Args:
        instance: كائن المستخدم (User).
        filename (str): اسم الملف الأصلي المرفوع.

    Returns:
        str: المسار الكامل داخل مجلد MEDIA_ROOT.
             مثال: users/profile_pictures/a3f1bc.../photo.jpg
    """
    ext = Path(filename).suffix.lower()          # استخراج الامتداد (.jpg, .png...)
    unique_filename = f'{uuid.uuid4().hex}{ext}'  # اسم عشوائي فريد
    return f'users/profile_pictures/{unique_filename}'


# -----------------------------------------------------------------------
# نموذج المستخدم - Custom User Model
# -----------------------------------------------------------------------

class User(AbstractUser):
    """
    نموذج المستخدم المخصص لمنصة التجارة الإلكترونية الجزائرية.

    يمتد من AbstractUser للحفاظ على جميع مزايا Django الافتراضية:
    المصادقة (Authentication)، الصلاحيات (Permissions)، الجلسات (Sessions)،
    مع إضافة حقول مخصصة تناسب السوق الجزائري.

    Attributes:
        phone_number (str): رقم هاتف جزائري، ضروري للتواصل مع شركات التوصيل.
        role (str): دور المستخدم على المنصة (عميل / بائع / مقدم خدمة).
        profile_picture (ImageField): صورة الملف الشخصي.
        wilaya (ForeignKey): مرتبط بنموذج Wilaya من تطبيق localization.
        is_verified (bool): حالة توثيق الحساب عبر رقم الهاتف أو البريد.

    Example:
        >>> user = User.objects.create_user(
        ...     username='ahmed_dz',
        ...     phone_number='0661234567',
        ...     role=User.Role.SELLER,
        ... )
        >>> user.is_seller
        True
    """

    # -------------------------------------------------------------------
    # الاختيارات الداخلية - Inner Choices Classes
    # -------------------------------------------------------------------

    class Role(models.TextChoices):
        """
        أدوار المستخدمين المتاحة على المنصة.

        - CUSTOMER : عميل عادي يتصفح ويشتري المنتجات والخدمات.
        - SELLER   : بائع يملك متجراً ويبيع منتجات مادية.
        - PROVIDER : مقدم خدمة (كهربائي، معلم خصوصي، صيانة...).
        """
        CUSTOMER = 'CUSTOMER', _('عميل')
        VENDOR = 'VENDOR', _('بائع/مقدم خدمة')
        INSTITUTION = 'INSTITUTION', _('مؤسسة')
        INCUBATOR = 'INCUBATOR', _('حاضنة جامعية')

    # -------------------------------------------------------------------
    # المحققات - Validators
    # -------------------------------------------------------------------

    algerian_phone_validator = RegexValidator(
        regex=r'^(\+213|0)(5|6|7)\d{8}$',
        message=_(
            'رقم الهاتف غير صحيح. يجب أن يبدأ بـ 05 أو 06 أو 07 '
            '(أو +2135 / +2136 / +2137). مثال: 0661234567'
        ),
    )

    # -------------------------------------------------------------------
    # الحقول المُضافة - Custom Fields
    # -------------------------------------------------------------------

    phone_number = models.CharField(
        verbose_name=_('رقم الهاتف'),
        max_length=15,
        unique=True,
        validators=[algerian_phone_validator],
        help_text=_('رقم هاتف جزائري فعّال. مثال: 0661234567'),
    )

    role = models.CharField(
        verbose_name=_('الدور'),
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True,  # فهرسة لتسريع الاستعلامات من نوع: filter(role=...)
    )

    university_name = models.CharField(
        _('اسم الجامعة'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('الجامعة التابعة لها الحاضنة')
    )

    profile_picture = models.ImageField(
        verbose_name=_('صورة الملف الشخصي'),
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
    )

    # استخدام ForeignKey لنموذج Wilaya من تطبيق localization
    # بدلاً من TextChoices لتجنب التكرار وتسهيل إدارة الولايات مركزياً
    wilaya = models.ForeignKey(
        'localization.Wilaya',
        verbose_name=_('الولاية'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_('الولاية الجزائرية، تُستخدم لحساب رسوم ومدة التوصيل'),
    )

    is_verified = models.BooleanField(
        verbose_name=_('حساب موثّق'),
        default=False,
        help_text=_('يصبح True بعد التحقق من رقم الهاتف أو البريد الإلكتروني'),
    )

    # حقول مخصصة للحاضنات والمؤسسات
    performance_score = models.PositiveIntegerField(
        verbose_name=_('درجة الأداء'),
        default=0,
        help_text=_('درجة تقييم أداء المؤسسة من 0 إلى 100')
    )
    incubator = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incubated_institutions',
        verbose_name=_('الحاضنة الوصية'),
        limit_choices_to={'role': Role.INCUBATOR}
    )

    # -------------------------------------------------------------------
    # إعدادات حقل المصادقة - Authentication Config
    # -------------------------------------------------------------------

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number', 'first_name', 'last_name']

    # -------------------------------------------------------------------
    # الإعدادات الوصفية - Meta
    # -------------------------------------------------------------------

    class Meta:
        verbose_name        = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        ordering            = ['-date_joined']

    # -------------------------------------------------------------------
    # الدوال - Methods
    # -------------------------------------------------------------------

    def __str__(self) -> str:
        return f'{self.get_full_name()} | {self.get_role_display()}'

    def get_full_name(self) -> str:
        """
        إرجاع الاسم الكامل (الأول + الأخير).
        إذا لم يُحدَّد الاسم، يُعاد اسم المستخدم (username) كبديل.
        """
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.username

    # --- خصائص التحقق السريع من الدور ---

    @property
    def is_customer(self) -> bool:
        """True إذا كان المستخدم عميلاً (مشترياً)."""
        return self.role == self.Role.CUSTOMER

    @property
    def is_vendor(self) -> bool:
        """True إذا كان المستخدم بائع منتجات أو مقدم خدمة."""
        return self.role == self.Role.VENDOR

    @property
    def is_institution(self) -> bool:
        return self.role == self.Role.INSTITUTION

    @property
    def is_incubator(self):
        return self.role == self.Role.INCUBATOR

    @property
    def can_list_items(self) -> bool:
        """
        True إذا كان بإمكان المستخدم نشر منتجات أو خدمات.
        يشترط أن يكون الحساب موثّقاً (is_verified=True).
        """
        return self.role in (self.Role.VENDOR,) and self.is_verified


class TeamMember(models.Model):
    """نموذج أعضاء فريق عمل (حاضنة أو مؤسسة)."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_members',
        help_text=_('المستخدم (الحاضنة أو المؤسسة) الذي ينتمي إليه هذا العضو')
    )
    name = models.CharField(_('الاسم الكامل'), max_length=255)
    position = models.CharField(_('المنصب/الدور'), max_length=255)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True, null=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True, null=True)
    bio = models.TextField(_('نبذة مختصرة'), blank=True, null=True)
    image = models.ImageField(_('الصورة'), upload_to='teams/members/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('عضو فريق')
        verbose_name_plural = _('أعضاء الفريق')

    def __str__(self):
        return f"{self.name} - {self.position} ({self.user.username})"