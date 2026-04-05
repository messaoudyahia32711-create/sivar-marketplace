from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ('action_time', 'user', 'content_type', 'action_flag')
    search_fields = ('object_repr', 'change_message')
    date_hierarchy = 'action_time'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    تخصيص لوحة تحكم المستخدم لإضافة الحقول الجديدة (الدور، الهاتف، الصورة).
    """
    # الأعمدة المعروضة في القائمة
    list_display = ('username', 'email', 'phone_number', 'role', 'wilaya', 'is_verified', 'is_active')

    # الفلاتر الجانبية
    list_filter = ('role', 'is_verified', 'is_staff', 'is_active', 'wilaya')

    # حقول البحث
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')

    # ترتيب الحقول في صفحة التعديل
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('المعلومات الشخصية'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role', 'wilaya')}),
        (_('الصورة الشخصية'), {'fields': ('profile_picture',)}),
        (_('التوثيق'), {'fields': ('is_verified',)}),
        (_('الصلاحيات'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('تواريخ مهمة'), {'fields': ('last_login', 'date_joined')}),
    )

    # الحقول المطلوبة عند إنشاء مستخدم جديد من لوحة التحكم
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )

    # حقول للقراءة فقط
    readonly_fields = ('date_joined', 'last_login')

    # الترتيب الافتراضي
    ordering = ('-date_joined',)