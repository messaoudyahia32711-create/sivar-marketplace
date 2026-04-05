import os
import django

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.vendors.models import Store

username = 'incubator_admin'
password = 'admin_pass_2024'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_user(
        username=username, 
        password=password, 
        role='INCUBATOR', 
        phone_number='0660112233',
        university_name='جامعة العلوم والتكنولوجيا هواري بومدين (USTHB)',
        is_verified=True
    )
    # Create a profile (using Store model for now as requested 'copy and modify')
    Store.objects.create(
        vendor=user,
        name='حاضنة الأعمال USTHB',
        description='الحاضنة الرسمية لدعم الابتكار والمؤسسات الناشئة.'
    )
    print(f"✅ تم إنشاء حساب الحاضنة بنجاح.")
else:
    print("⚠️ حساب الحاضنة موجود مسبقاً.")
