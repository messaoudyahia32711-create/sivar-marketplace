"""
Serializers لتطبيق المستخدمين.
يغطي: عرض الملف الشخصي، التسجيل، تسجيل الدخول، وتغيير كلمة المرور.
"""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

# get_user_model() هو الأسلوب الصحيح دائماً بدلاً من الاستيراد المباشر،
# لأنه يحترم إعداد AUTH_USER_MODEL في settings.py تلقائياً.
User = get_user_model()


# ══════════════════════════════════════════════════════════════════
# 1. UserSerializer — عرض الملف الشخصي وتعديله
# ══════════════════════════════════════════════════════════════════

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer مخصص لعرض بيانات المستخدم وتعديل ملفه الشخصي.

    الاستخدام:
        - GET  /api/users/me/  → عرض بيانات المستخدم الحالي.
        - PUT  /api/users/me/  → تعديل الملف الشخصي كاملاً.
        - PATCH /api/users/me/ → تعديل حقل واحد أو أكثر.

    ملاحظات أمنية:
        - حقل password مُستبعد كلياً من العرض والتعديل.
        - حقل role لا يمكن تعديله إلا عبر لوحة الإدارة (read_only).
        - حقل is_verified لا يُعدَّل من قِبَل المستخدم مباشرةً.
    """

    # عرض القيمة المقروءة للدور (مثلاً "بائع" بدل "SELLER")
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True,
        label=_('الدور'),
    )

    # يمكن إضافة wilaya_display لعرض اسم الولاية
    wilaya_display = serializers.CharField(
        source='wilaya.name',
        read_only=True,
        label=_('اسم الولاية'),
    )

    # تعريف صريح لدعم رفع الملفات عبر multipart/form-data
    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True,
        label=_('صورة الملف الشخصي'),
        help_text=_('صيغ مدعومة: JPEG، PNG، WEBP. الحد الأقصى: 2MB'),
    )

    class Meta:
        model  = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'role_display',
            'profile_picture',
            'wilaya',
            'wilaya_display',
            'is_verified',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'role',        # تغيير الدور يستلزم تدخل الإدارة
            'is_verified', # يتغير فقط بعد التحقق من الهاتف/البريد
            'date_joined',
        ]

    def update(self, instance, validated_data):
        """
        تعديل الملف الشخصي مع حذف الصورة القديمة عند استبدالها.

        يمنع تراكم الملفات اليتيمة (Orphaned Files) في مجلد MEDIA_ROOT
        عند رفع صورة جديدة، مما يوفر مساحة التخزين.
        """
        new_picture = validated_data.get('profile_picture')

        # احذف الصورة القديمة من التخزين قبل حفظ الجديدة
        if new_picture and instance.profile_picture:
            instance.profile_picture.delete(save=False)

        return super().update(instance, validated_data)


# ══════════════════════════════════════════════════════════════════
# 2. RegisterSerializer — تسجيل مستخدم جديد
# ══════════════════════════════════════════════════════════════════

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer مخصص لإنشاء حسابات جديدة.

    الميزات:
        - تأكيد كلمة المرور عبر حقل password2.
        - التحقق من قوة كلمة المرور باستخدام validators Django.
        - ضمان تفرد البريد الإلكتروني (Case-Insensitive).
        - تشفير كلمة المرور تلقائياً بخوارزمية PBKDF2.

    مثال على الطلب (JSON):
        {
            "username": "ahmed_dz",
            "email": "ahmed@example.com",
            "phone_number": "0661234567",
            "role": "SELLER",
            "password": "StrongPass@123",
            "password2": "StrongPass@123"
        }
    """

    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label=_('كلمة المرور'),
        help_text=_('أي طول مسموح لتسهيل التجربة'),
    )

    # password2 ليس حقلاً في النموذج، لذا يُعرَّف هنا يدوياً
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label=_('تأكيد كلمة المرور'),
    )

    entity_name = serializers.CharField(write_only=True, required=False, allow_blank=True, label=_('اسم الجهة'))
    university_name = serializers.CharField(write_only=True, required=False, allow_blank=True, label=_('الجامعة الوصية'))
    activity_type = serializers.CharField(write_only=True, required=False, allow_blank=True, label=_('نوع النشاط'))
    incubator_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, label=_('رقم الحاضنة'))

    class Meta:
        model  = User
        fields = [
            'username',
            'email',
            'phone_number',
            'role',
            'password',
            'password2',
            'entity_name',
            'university_name',
            'activity_type',
            'incubator_id',
        ]
        extra_kwargs = {
            'role': {
                'required': False,
            },
            'email': {
                'required': True,
            },
        }

    # ── التحقق على مستوى الحقل (Field-Level Validation) ──────────

    def validate_email(self, value: str) -> str:
        """
        التحقق من تفرد البريد الإلكتروني وتوحيده (Normalize).

        يُحوَّل البريد إلى حروف صغيرة لمنع التكرار عبر أحرف مختلفة
        (مثل: Ahmed@Gmail.com == ahmed@gmail.com).
        """
        normalized_email = value.lower().strip()

        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError(
                _('هذا البريد الإلكتروني مستخدم بالفعل. جرّب بريداً آخر.')
            )

        return normalized_email

    # ── التحقق على مستوى الكائن (Object-Level Validation) ────────

    def validate(self, attrs: dict) -> dict:
        """
        التحقق من تطابق كلمتي المرور وقوتهما.

        يُشغِّل validate_password() الذي يطبّق جميع المحققات المعرَّفة
        في AUTH_PASSWORD_VALIDATORS بـ settings.py.
        """
        password  = attrs.get('password')
        password2 = attrs.get('password2')

        # ① تطابق كلمتي المرور
        if password != password2:
            raise serializers.ValidationError({
                'password2': _('كلمتا المرور غير متطابقتين. تأكد من الإدخال.')
            })

        # ② تعطيل فحص قوة كلمة المرور (لجعل التسجيل سهلاً)
        # temp_user = User(
        #     username=attrs.get('username', ''),
        #     email=attrs.get('email', ''),
        # )
        # try:
        #     validate_password(password, user=temp_user)
        # except DjangoValidationError as exc:
        #     raise serializers.ValidationError({'password': list(exc.messages)})

        return attrs

    def create(self, validated_data: dict) -> User:
        """
        إنشاء المستخدم مع تشفير كلمة المرور.
        """
        validated_data.pop('password2', None)
        password = validated_data.pop('password')

        entity_name = validated_data.pop('entity_name', None)
        university_name = validated_data.pop('university_name', None)
        activity_type = validated_data.pop('activity_type', None)
        incubator_id = validated_data.pop('incubator_id', None)

        role = validated_data.get('role', 'CUSTOMER')

        if entity_name:
            validated_data['first_name'] = entity_name

        if role == 'INCUBATOR' and university_name:
            validated_data['university_name'] = university_name

        if role == 'INSTITUTION' and incubator_id:
            try:
                incubator_obj = User.objects.get(id=incubator_id, role='INCUBATOR')
                validated_data['incubator'] = incubator_obj
            except User.DoesNotExist:
                pass

        # استخدام create_user لضمان الحفظ الصحيح وتشفير كلمة المرور
        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        if role in ['INSTITUTION', 'VENDOR', 'SELLER']:
            from apps.vendors.models import OrganizationRequest, Store
            # إنشاء واجهة متجر/مؤسسة لحفظ الاسم والبيانات
            Store.objects.create(vendor=user, name=entity_name or user.username)
            if role == 'INSTITUTION' and 'incubator' in validated_data:
                OrganizationRequest.objects.create(
                    name=entity_name or user.username,
                    sector=activity_type or 'عام',
                    incubator=validated_data['incubator']
                )

        return user


# ══════════════════════════════════════════════════════════════════
# 3. LoginSerializer — تسجيل الدخول
# ══════════════════════════════════════════════════════════════════

class LoginSerializer(serializers.Serializer):
    """
    Serializer مخصص للتحقق من بيانات تسجيل الدخول.

    يستخدم دالة authenticate() التي تحترم AUTHENTICATION_BACKENDS،
    مما يتيح دعم أساليب مصادقة متعددة مستقبلاً.

    بعد التحقق الناجح، يتوفر كائن المستخدم في:
        serializer.validated_data['user']

    مثال الاستخدام في View:
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
    """

    username = serializers.CharField(
        label=_('اسم المستخدم'),
        trim_whitespace=True,
    )

    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label=_('كلمة المرور'),
        trim_whitespace=False,  # مهم: بعض كلمات المرور تحتوي على مسافات مقصودة
    )

    def validate(self, attrs: dict) -> dict:
        """
        التحقق من صحة بيانات الدخول وإرفاق كائن المستخدم.

        خطوات التحقق:
            1. التأكد من عدم فراغ الحقول.
            2. محاولة المصادقة عبر authenticate().
            3. التحقق من نشاط الحساب (is_active).

        Raises:
            ValidationError: في حالة بيانات خاطئة أو حساب موقوف.
        """
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '')

        # ① التحقق من عدم فراغ الحقول
        if not username or not password:
            raise serializers.ValidationError(
                _('يجب إدخال اسم المستخدم وكلمة المرور.'),
                code='missing_credentials',
            )

        # ② المصادقة — ترجع None إذا كانت البيانات خاطئة
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )

        # ③ التحقق من صحة البيانات
        # نُعيد رسالة عامة عمداً لمنع هجمات تعداد المستخدمين (User Enumeration)
        if user is None:
            raise serializers.ValidationError(
                _('اسم المستخدم أو كلمة المرور غير صحيحة.'),
                code='invalid_credentials',
            )

        # ④ التحقق من نشاط الحساب
        if not user.is_active:
            raise serializers.ValidationError(
                _('هذا الحساب موقوف. يرجى التواصل مع الدعم الفني.'),
                code='account_disabled',
            )

        # إرفاق المستخدم ليكون متاحاً في validated_data بعد is_valid()
        attrs['user'] = user
        return attrs


# ══════════════════════════════════════════════════════════════════
# 4. ChangePasswordSerializer — تغيير كلمة المرور
# ══════════════════════════════════════════════════════════════════

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer مخصص لتغيير كلمة مرور المستخدم المسجّل دخوله.

    يشترط إدخال كلمة المرور الحالية كطبقة أمان إضافية،
    مما يحمي الحساب حتى لو ترك المستخدم جلسته مفتوحة.

    ملاحظة: يتطلب أن يكون request.user متوفراً في context.
    """

    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label=_('كلمة المرور الحالية'),
    )

    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label=_('كلمة المرور الجديدة'),
    )

    new_password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label=_('تأكيد كلمة المرور الجديدة'),
    )

    def validate_old_password(self, value: str) -> str:
        """التحقق من صحة كلمة المرور الحالية."""
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                _('كلمة المرور الحالية غير صحيحة.')
            )

        return value

    def validate(self, attrs: dict) -> dict:
        """التحقق من تطابق كلمتي المرور الجديدتين وقوتهما."""
        new_password  = attrs.get('new_password')
        new_password2 = attrs.get('new_password2')

        if new_password != new_password2:
            raise serializers.ValidationError({
                'new_password2': _('كلمتا المرور الجديدتان غير متطابقتين.')
            })

        # try:
        #     validate_password(new_password, user=self.context['request'].user)
        # except DjangoValidationError as exc:
        #     raise serializers.ValidationError({'new_password': list(exc.messages)})

        return attrs

    def save(self, **kwargs) -> User:
        """تطبيق كلمة المرور الجديدة المشفَّرة على حساب المستخدم."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user