"""
URL Configuration لتطبيق المستخدمين.
يُضاف هذا الملف إلى urls.py الرئيسي عبر:
    path('api/users/', include('apps.users.urls'))
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # تسجيل مستخدم جديد
    path('register/', views.register_view, name='register'),

    # تسجيل الدخول
    path('login/', views.login_view, name='login'),

    # تسجيل الخروج (يتطلب تسجيل دخول)
    path('logout/', views.logout_view, name='logout'),

    # عرض وتعديل الملف الشخصي (يتطلب تسجيل دخول)
    path('profile/', views.profile_view, name='profile'),

    # تغيير كلمة المرور (يتطلب تسجيل دخول)
    path('change-password/', views.change_password_view, name='change-password'),
]