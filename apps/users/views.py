"""
Views لتطبيق المستخدمين — نظام إدارة المتجر الإلكتروني.

الـ Endpoints المُغطاة:
    POST   /api/users/register/         ← تسجيل حساب جديد
    POST   /api/users/login/            ← تسجيل الدخول
    POST   /api/users/logout/           ← تسجيل الخروج
    GET    /api/users/profile/          ← عرض الملف الشخصي
    PUT    /api/users/profile/          ← تعديل الملف الشخصي (كامل)
    PATCH  /api/users/profile/          ← تعديل الملف الشخصي (جزئي)
    PUT    /api/users/change-password/  ← تغيير كلمة المرور
"""

import logging

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

# ── Logger مخصص لهذا الملف (يكتب في ملف السجلات عند وقوع أخطاء) ──
logger = logging.getLogger(__name__)

User = get_user_model()


# ══════════════════════════════════════════════════════════════════
# 1. Register View — تسجيل مستخدم جديد
# ══════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    إنشاء حساب مستخدم جديد وإرجاع التوكن فور التسجيل.

    الأمان:
        - كلمة المرور مشفرة بـ PBKDF2 قبل الحفظ (عبر RegisterSerializer).
        - يُنشأ التوكن مباشرةً بعد التسجيل لتجنب خطوة تسجيل دخول إضافية.

    Method : POST
    URL    : /api/users/register/
    Auth   : AllowAny (لا يحتاج مصادقة)

    Request Body (JSON):
        {
            "username"     : "ahmed_dz",
            "email"        : "ahmed@example.com",
            "phone_number" : "0661234567",
            "role"         : "CUSTOMER",
            "password"     : "StrongPass@123",
            "password2"    : "StrongPass@123"
        }

    Response 201:
        {
            "message" : "تم إنشاء الحساب بنجاح",
            "token"   : "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            "user"    : { ... }
        }

    Response 400:
        {
            "message" : "فشل إنشاء الحساب",
            "errors"  : { "email": ["هذا البريد مستخدم بالفعل"] }
        }
    """
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'message': 'فشل إنشاء الحساب. يرجى مراجعة البيانات المدخلة.',
                'errors' : serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ① حفظ المستخدم — يُنفِّذ create() في RegisterSerializer
    #   (يشمل تشفير كلمة المرور تلقائياً بـ set_password)
    user = serializer.save()

    # ② إنشاء Token للمستخدم الجديد
    #   get_or_create يمنع التكرار في حالة الاستدعاء المزدوج
    token, _ = Token.objects.get_or_create(user=user)

    # ③ بيانات المستخدم للرد (context لتوليد روابط مطلقة للصور)
    user_data = UserSerializer(user, context={'request': request}).data

    logger.info('New user registered: %s (id=%s)', user.username, user.pk)

    return Response(
        {
            'message': 'تم إنشاء الحساب بنجاح. مرحباً بك! 🎉',
            'token'  : token.key,
            'user'   : user_data,
        },
        status=status.HTTP_201_CREATED,
    )


# ══════════════════════════════════════════════════════════════════
# 2. Login View — تسجيل الدخول
# ══════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    التحقق من بيانات الدخول وإرجاع التوكن والمستخدم.

    الأمان:
        - المصادقة تتم عبر authenticate() الذي يقاوم هجمات Timing Attack.
        - رسالة الخطأ عامة عمداً لمنع هجمات User Enumeration.
        - get_or_create يمنع إنشاء توكنات مكررة.

    Method : POST
    URL    : /api/users/login/
    Auth   : AllowAny (لا يحتاج مصادقة)

    Request Body (JSON):
        {
            "username" : "ahmed_dz",
            "password" : "StrongPass@123"
        }

    Response 200:
        {
            "message" : "أهلاً ahmed_dz! تم تسجيل دخولك بنجاح.",
            "token"   : "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            "user"    : { ... }
        }

    Response 400:
        {
            "message" : "فشل تسجيل الدخول",
            "errors"  : { "non_field_errors": ["اسم المستخدم أو كلمة المرور غير صحيحة"] }
        }
    """
    serializer = LoginSerializer(
        data=request.data,
        # context مطلوب لتمرير request إلى authenticate() داخل LoginSerializer
        context={'request': request},
    )

    if not serializer.is_valid():
        return Response(
            {
                'message': 'فشل تسجيل الدخول. يرجى مراجعة البيانات المدخلة.',
                'errors' : serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ① استخراج المستخدم من validated_data
    #   (يُعيَّن في LoginSerializer.validate() بعد نجاح authenticate)
    user = serializer.validated_data['user']

    # ② جلب أو إنشاء توكن للمستخدم
    token, created = Token.objects.get_or_create(user=user)

    # ③ بيانات المستخدم الكاملة للرد
    user_data = UserSerializer(user, context={'request': request}).data

    action = 'logged in (new token)' if created else 'logged in (existing token)'
    logger.info('User %s (id=%s): %s', user.username, user.pk, action)

    return Response(
        {
            'message': f'أهلاً {user.username}! تم تسجيل دخولك بنجاح.',
            'token'  : token.key,
            'user'   : user_data,
        },
        status=status.HTTP_200_OK,
    )


# ══════════════════════════════════════════════════════════════════
# 3. Logout View — تسجيل الخروج
# ══════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    إلغاء صلاحية التوكن الحالي وتسجيل خروج المستخدم.

    يحذف التوكن من قاعدة البيانات بدلاً من إخفائه فقط،
    مما يُبطل أي طلب مستقبلي يحمل هذا التوكن حتى لو سُرق.

    Method : POST
    URL    : /api/users/logout/
    Auth   : IsAuthenticated

    Headers:
        Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

    Response 200:
        { "message": "تم تسجيل الخروج بنجاح" }
    """
    try:
        # حذف التوكن المرتبط بالمستخدم الحالي
        request.user.auth_token.delete()
        logger.info('User %s (id=%s) logged out.', request.user.username, request.user.pk)
    except Token.DoesNotExist:
        # المستخدم لا يملك توكناً — الخروج ناجح على أي حال
        pass

    return Response(
        {'message': 'تم تسجيل الخروج بنجاح. إلى اللقاء! 👋'},
        status=status.HTTP_200_OK,
    )


# ══════════════════════════════════════════════════════════════════
# 4. Profile View — عرض وتعديل الملف الشخصي
# ══════════════════════════════════════════════════════════════════

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    عرض وتعديل بيانات المستخدم المسجّل حالياً.

    GET   → يُرجع البيانات الكاملة للمستخدم الحالي.
    PUT   → يُعدِّل الملف الشخصي (يتطلب جميع الحقول القابلة للتعديل).
    PATCH → يُعدِّل حقلاً واحداً أو أكثر (Partial Update).

    رفع الصور:
        استخدم Content-Type: multipart/form-data عند إرسال profile_picture.
        DRF يدمج request.data + request.FILES تلقائياً.

    Method : GET | PUT | PATCH
    URL    : /api/users/profile/
    Auth   : IsAuthenticated

    Headers:
        Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

    مثال PATCH Request (multipart/form-data):
        first_name      = أحمد
        phone_number    = 0771234567
        profile_picture = [ملف صورة]

    Response GET (200):
        { "id": 1, "username": "ahmed_dz", "email": "...", ... }

    Response PUT/PATCH (200):
        {
            "message" : "تم تحديث الملف الشخصي بنجاح",
            "user"    : { ... }
        }

    Response 400:
        {
            "message" : "فشل التحديث",
            "errors"  : { "phone_number": ["أدخل رقم هاتف صالح"] }
        }
    """
    user = request.user  # المستخدم الحالي المصادَق عليه من التوكن

    # ── GET: عرض الملف الشخصي ────────────────────────────────────
    if request.method == 'GET':
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ── PUT / PATCH: تعديل الملف الشخصي ──────────────────────────
    #
    # partial=True في PATCH يتيح تعديل حقل واحد فقط دون إرسال بقية الحقول.
    # partial=False في PUT يتطلب إرسال جميع الحقول القابلة للتعديل.
    is_partial = (request.method == 'PATCH')

    serializer = UserSerializer(
        instance=user,
        data=request.data,      # يشمل request.FILES تلقائياً في DRF
        partial=is_partial,
        context={'request': request},
    )

    if not serializer.is_valid():
        return Response(
            {
                'message': 'فشل تحديث الملف الشخصي. يرجى مراجعة البيانات.',
                'errors' : serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # يُنفِّذ update() في UserSerializer (يشمل حذف الصورة القديمة)
    serializer.save()

    logger.info(
        'User %s (id=%s) updated profile [%s].',
        user.username, user.pk, request.method,
    )

    return Response(
        {
            'message': 'تم تحديث الملف الشخصي بنجاح. ✅',
            'user'   : serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ══════════════════════════════════════════════════════════════════
# 5. Change Password View — تغيير كلمة المرور
# ══════════════════════════════════════════════════════════════════

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    تغيير كلمة مرور المستخدم المسجّل مع إبطال التوكن الحالي.

    بعد تغيير كلمة المرور بنجاح:
        1. يُحذف التوكن الحالي لإبطال الجلسة الحالية.
        2. يجب على المستخدم تسجيل الدخول مجدداً للحصول على توكن جديد.

    هذا السلوك يحمي الحساب في حالة سرقة التوكن القديم.

    Method : PUT
    URL    : /api/users/change-password/
    Auth   : IsAuthenticated

    Request Body (JSON):
        {
            "old_password"  : "OldPass@123",
            "new_password"  : "NewPass@456",
            "new_password2" : "NewPass@456"
        }

    Response 200:
        { "message": "تم تغيير كلمة المرور بنجاح. يرجى تسجيل الدخول مجدداً." }

    Response 400:
        {
            "message" : "فشل تغيير كلمة المرور",
            "errors"  : { "old_password": ["كلمة المرور الحالية غير صحيحة"] }
        }
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request},  # مطلوب للوصول إلى request.user داخل الـ Serializer
    )

    if not serializer.is_valid():
        return Response(
            {
                'message': 'فشل تغيير كلمة المرور. يرجى مراجعة البيانات.',
                'errors' : serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ① تطبيق كلمة المرور الجديدة وتشفيرها (عبر set_password في ChangePasswordSerializer.save)
    serializer.save()

    # ② حذف التوكن الحالي لإجبار إعادة تسجيل الدخول
    #    يُبطل كل الجلسات النشطة الأخرى لنفس المستخدم (أمان إضافي)
    try:
        request.user.auth_token.delete()
    except Token.DoesNotExist:
        pass

    logger.info(
        'User %s (id=%s) changed password. Token invalidated.',
        request.user.username, request.user.pk,
    )

    return Response(
        {
            'message': (
                'تم تغيير كلمة المرور بنجاح. 🔒 '
                'يرجى تسجيل الدخول مجدداً باستخدام كلمة المرور الجديدة.'
            )
        },
        status=status.HTTP_200_OK,
    )


# ══════════════════════════════════════════════════════════════════
# 6. UI Render Views — عرض صفحات المصادقة المركزية (Templates)
# ══════════════════════════════════════════════════════════════════

from django.shortcuts import render, redirect

def login_page_view(request):
    """
    عرض صفحة تسجيل الدخول المركزية (UI).
    التوجيه يتم عبر الجافاسكريبت بعد نجاح طلب الـ API.
    """
    if request.user.is_authenticated and not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return redirect('dashboard-redirect')
        
    return render(request, 'pages/login.html')

def dashboard_redirect_view(request):
    """
    يوجه المستخدم المسجل إلى لوحة التحكم الخاصة به بناءً على دوره.
    إذا كان لديه توكن مخزن في الجلسة، يتم تمريره لتسهيل عملية الدخول الموحدة (SSO).
    """
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    token, _ = Token.objects.get_or_create(user=user)
    
    # تحديد المنفذ حسب الدور (Port Mapping)
    ports = {
        'VENDOR': '5175',
        'SELLER': '5175',
        'INSTITUTION': '5174',
        'INCUBATOR': '5177',
        'CUSTOMER': '5176'
    }
    
    role = getattr(user, 'role', 'CUSTOMER')
    port = ports.get(role, '5176')
    
    if user.is_superuser:
        return redirect('/admin/')
        
    return redirect(f'http://localhost:{port}/login?token={token.key}')

def register_page_view(request):
    """
    عرض صفحة إنشاء حساب جديد المركزية (UI).
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    incubators = User.objects.filter(role='INCUBATOR', is_active=True)
    return render(request, 'pages/register.html', {'incubators': incubators})