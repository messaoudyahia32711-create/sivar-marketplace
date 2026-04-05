import random
import os
import shutil
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings

from apps.users.models import User
from apps.products.models import Product, Category
from apps.services.models import Service, ServiceCategory
from apps.orders.models import Order
from apps.reviews.models import Review
from apps.vendors.models import Store


class Command(BaseCommand):
    help = 'تعبئة قاعدة البيانات بالحاضنات والمؤسسات والمتاجر (بيانات تجريبية دقيقة)'

    def generate_unique_phone(self):
        """Generates a random unique Algerian phone number"""
        while True:
            phone = f'06{''.join([str(random.randint(0, 9)) for _ in range(8)])}'
            if not User.objects.filter(phone_number=phone).exists():
                return phone

    def handle(self, *args, **kwargs):
        self.stdout.write("[CLEAN] Cleaning old test data...")
        Review.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Service.objects.all().delete()
        Category.objects.all().delete()
        ServiceCategory.objects.all().delete()
        Store.objects.all().delete()
        User.objects.filter(is_staff=False).delete()

        # ═══════════════════════════════════════════════════════════
        # 1. إنشاء الحسابات: حاضنات الأعمال
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[USERS] Creating Incubators...")

        inc_alger, _ = User.objects.get_or_create(
            username='incubator_alger3', role='INCUBATOR',
            defaults={
                'first_name': 'حاضنة أعمال جامعة الجزائر 3',
                'university_name': 'جامعة الجزائر 3',
                'phone_number': self.generate_unique_phone()
            }
        )
        inc_alger.set_password('SivarAlger3_2026')
        inc_alger.save()

        inc_soukahras, _ = User.objects.get_or_create(
            username='incubator_soukahras', role='INCUBATOR',
            defaults={
                'first_name': 'حاضنة أعمال جامعة سوق أهراس',
                'university_name': 'جامعة محمد الشريف مساعدية سوق أهراس',
                'phone_number': self.generate_unique_phone()
            }
        )
        inc_soukahras.set_password('SivarSoukAhras_2026')
        inc_soukahras.save()

        # ═══════════════════════════════════════════════════════════
        # 2. إنشاء المؤسسات التابعة للحاضنات
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[USERS] Creating Institutions...")

        institutions_data = [
            # Taba lialger 3
            {
                'username': 'shifa_wellness', 'name': 'واحة الشفاء', 'incubator': inc_alger,
                'desc': 'مركز استشفاء في قلب العاصمة يقدم تجربة علاجية متكاملة لساكني أحياء بن عكنون وحمام ملوان.'
            },
            {
                'username': 'naqaha_center', 'name': 'النقاهة الذهبية', 'incubator': inc_alger,
                'desc': 'مؤسسة طبية راقية تقدم خدماتها لسكان الشراقة وحيدرة، متخصصة في النقاهة ما بعد العمليات.'
            },
            {
                'username': 'sahara_therapy', 'name': 'رمال الشفاء', 'incubator': inc_alger,
                'desc': 'مشروع مدعوم من العاصمة لتقديم العلاج بالرمال في تيميمون وغرداية لتنشيط السياحة العلاجية الجنوبية.'
            },
            # Taba li Souk ahras
            {
                'username': 'hammam_thagaste', 'name': 'ينابيع تاغاست', 'incubator': inc_soukahras,
                'desc': 'مؤسسة تستغل المياه المعدنية في حمام النبايل (تاورة) مع تنظيم رحلات لمدينة سدراتة الأثرية وآثار خميسة.'
            },
            {
                'username': 'rouhi_clinic', 'name': 'روحي للطب التكميلي', 'incubator': inc_soukahras,
                'desc': 'أول عيادة متخصصة في الطب التكميلي تتوسط مدينة سدراتة وتفرع في وسط سوق أهراس.'
            },
            {
                'username': 'atlas_wellbeing', 'name': 'أطلس العافية', 'incubator': inc_soukahras,
                'desc': 'محطة علاجية تغطي الشرق الجزائري (سوق أهراس، سدراتة) ممتدة إلى حمام دباغ بقالمة وحمام الصالحين بخنشلة.'
            },
        ]

        institutions = []
        for inst in institutions_data:
            user, _ = User.objects.get_or_create(
                username=inst['username'], 
                role='INSTITUTION',
                defaults={
                    'first_name': inst['name'], 
                    'incubator': inst['incubator'],
                    'phone_number': self.generate_unique_phone()
                }
            )
            user.is_verified = True
            user.performance_score = random.randint(85, 98)
            user.set_password('Institution_2026')
            user.save()
            
            # Create a store/profile for the institution so they can attach services/desc
            Store.objects.create(
                vendor=user, name=inst['name'], description=inst['desc'],
                is_verified=True
            )
            institutions.append(user)

        # ═══════════════════════════════════════════════════════════
        # 3. إنشاء المتاجر (التجار) وربطها بمتاجر فعلية
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[USERS] Creating Vendors...")

        vendors_data = [
            {'username': 'store_med_care', 'name': 'ميد كير للمستلزمات', 'location': 'العاصمة - ساحة أول ماي', 'desc': 'متجر متخصص بجميع المستلزمات الطبية المنزلية والصحية.'},
            {'username': 'store_nature_secret', 'name': 'أسرار الطبيعة', 'location': 'جيجل', 'desc': 'أفضل المنتجات الطبيعية المستخلصة من أعشاب جبال جيجل الساحرة.'},
            {'username': 'store_sahara_health', 'name': 'صحة الصحراء', 'location': 'الوادي - مدينة الألف قبة', 'desc': 'منتجات تمور طبية ومستخلصات نباتية صحراوية أصلية.'},
            {'username': 'store_east_pharma', 'name': 'أوراس فارما', 'location': 'خنشلة - جبال الأوراس', 'desc': 'منتجات تجميل طبيعية بمكونات من أعماق أوراس الأشم.'},
            {'username': 'store_sedrata_bio', 'name': 'سدراتة بيو', 'location': 'سوق أهراس - سدراتة', 'desc': 'متجر معتمد يوفر منتجات طبيعية وعسل صافي من أرياف سدراتة الجميلة.'},
        ]

        vendors = []
        for v in vendors_data:
            user, _ = User.objects.get_or_create(
                username=v['username'], role='SELLER',
                defaults={
                    'first_name': v['name'],
                    'phone_number': self.generate_unique_phone()
                }
            )
            user.is_verified = True
            user.set_password('Vendor_2026')
            user.save()
            
            Store.objects.create(
                vendor=user, name=v['name'], 
                location_detail=v['location'],
                description=v['desc'], is_verified=True
            )
            vendors.append(user)
            
        # إضافة مستخدمين كعملاء
        customers = []
        for i in range(5):
            c, _ = User.objects.get_or_create(
                username=f'customer_{i}', role='CUSTOMER', 
                defaults={
                    'first_name': f'مستخدم {i}',
                    'phone_number': self.generate_unique_phone()
                }
            )
            c.set_password('Sivar2024!')
            c.save()
            customers.append(c)

        # ═══════════════════════════════════════════════════════════
        # 4. التصنيفات
        # ═══════════════════════════════════════════════════════════
        cat_health = Category.objects.create(name='المنتجات الصحية', slug='health-products')
        cat_skincare = Category.objects.create(name='العناية بالبشرة', slug='skin-care', parent=cat_health)
        cat_supplements = Category.objects.create(name='مكملات وتغذية', slug='supplements', parent=cat_health)

        scat_medical = ServiceCategory.objects.create(name='السياحة العلاجية', slug='medical-tourism')
        scat_rehab = ServiceCategory.objects.create(name='إعادة التأهيل', slug='rehab')

        # ═══════════════════════════════════════════════════════════
        # 5. الخدمات (مرتبطة بالمؤسسات) وصورها
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[SERVICES] Creating Services...")

        services_config = [
            # واحة الشفاء (بن عكنون)
            {'vendor': institutions[0], 'cat': scat_rehab, 'name': 'جلسات استرخاء وعلاج طبيعي متكاملة', 'price': 8000, 
             'desc': 'حزم علاجية فاخرة في مرافقنا ببن عكنون، واستكمالات في حمامات طبيعية في البليدة. نقدم لعملائنا في العاصمة أفضل تجربة استشفاء مريحة.'},
            # النقاهة الذهبية (شراقة/حيدرة)
            {'vendor': institutions[1], 'cat': scat_medical, 'name': 'برنامج النقاهة المتقدم للمسنين', 'price': 15000, 
             'desc': 'برنامج نقاهة طويل الأمد يخدم سكان شراقة وحيدرة. يشمل الفحوصات الدورية والتغذية السليمة ضمن بيئة هادئة ومريحة للمريض.'},
            # رمال الشفاء (تيميمون/غرداية)
            {'vendor': institutions[2], 'cat': scat_medical, 'name': 'جلسات العلاج بالرمال الصحراوية', 'price': 45000, 
             'desc': 'رحلة استشفائية من مطار هواري بومدين بالعاصمة نحو تيميمون وغرداية لتلقي العلاج الطبيعي بالرمال الساخنة لمعالجة أمراض الروماتيزم.'},
            # ينابيع تاغاست (سوق أهراس/سدراتة)
            {'vendor': institutions[3], 'cat': scat_medical, 'name': 'سياحة معدنية وتاريخية بسوق أهراس', 'price': 25000, 
             'desc': 'العلاج بمياه حمام النبايل التاريخية مع جولات للاسترخاء في المسارات السياحية لمدينة سدراتة الأثرية وآثار خميسة المذهلة.'},
            # روحي للطب التكميلي (سدراتة)
            {'vendor': institutions[4], 'cat': scat_rehab, 'name': 'طب بديل وتدليك علاجي للرياضيين', 'price': 6000, 
             'desc': 'أول عيادة بمدينة سدراتة تقدم التدليك العلاجي للرياضيين، مع برامج للتعافي والإبر الصينية لجميع الوافدين من أحياء وسط سوق أهراس وخارجها.'},
            # أطلس العافية (قالمة/خنشلة)
            {'vendor': institutions[5], 'cat': scat_rehab, 'name': 'برنامج المسار الأوراسي للاستشفاء', 'price': 55000, 
             'desc': 'برنامج علاجي يبدأ من مركزنا في سدراتة شرقاً، وينتقل لـ حمام دباغ (98 درجة) بقالمة، ثم حمام الصالحين الأثري العريق بخنشلة بجبال الأوراس.'},
        ]

        # الصور التجريبية للخدمات
        demo_service_images = [
            'demo/services/458529.jpeg.webp',
            'demo/services/f1315253169b4023bad01b.jpg',
            'demo/services/images (1).jpg',
            'demo/services/images (2).jpg',
            'demo/services/images.jpg',
            'demo/services/مراكز-علاج-الادمان-في-الجزائر.jpg',
        ]

        for i, s in enumerate(services_config):
            # ربط الصورة
            img_source = demo_service_images[i % len(demo_service_images)]
            slug = slugify(s['name'], allow_unicode=True) or f"service-{i}"
            ext = os.path.splitext(img_source)[1]
            dest_relative = f'services/{slug}/main{ext}'
            dest_full = os.path.join(settings.MEDIA_ROOT, dest_relative)
            os.makedirs(os.path.dirname(dest_full), exist_ok=True)
            source_full = os.path.join(settings.MEDIA_ROOT, img_source)
            if os.path.exists(source_full):
                shutil.copy2(source_full, dest_full)

            Service.objects.create(
                vendor=s['vendor'],
                category=s['cat'],
                name=s['name'],
                description=s['desc'],
                price=Decimal(str(s['price'])),
                is_active=True,
                image_main=dest_relative if os.path.exists(source_full) else None,
            )

        # ═══════════════════════════════════════════════════════════
        # 6. المنتجات وصورها
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[PRODUCTS] Creating Products...")

        products_config = [
            {'vendor': vendors[0], 'cat': cat_supplements, 'name': 'مكمل غذائي بتركيبة الفيتامينات الكاملة', 'price': 4200, 
             'desc': 'المنتج المناسب لتعزيز المناعة اليومية. متاح في متجر ميد كير بالجزائر العاصمة مع شحن سريع لكل الولايات.'},
            
            {'vendor': vendors[1], 'cat': cat_skincare, 'name': 'زيت الضرو الطبيعي من أعالي جيجل', 'price': 1800, 
             'desc': 'زيت طبيعي 100% مستخلص من بذور الضرو الجيجلية المعروفة بخصائصها العلاجية لشفاء الحروق والجروح ومشاكل التنفس.'},
            
            {'vendor': vendors[2], 'cat': cat_skincare, 'name': 'مقشر رمال الصحراء بزيت النخيل', 'price': 2500, 
             'desc': 'منتج حصري من مدينة التمور الوادي. مقشر طبيعي للجلد غني بخلاصة التمر وزيت النخيل، يمنح البشرة لمعاناً ونضارة استثنائية.'},
            
            {'vendor': vendors[3], 'cat': cat_supplements, 'name': 'عسل السدر الأوراسي الأصلي', 'price': 9000, 
             'desc': 'عسل سدر خالص بضمان الجودة العالية، مقطوف مباشرة من مناحل خنشلة في سفوح جبال الأوراس الشاهقة.'},
            
            {'vendor': vendors[4], 'cat': cat_skincare, 'name': 'غسول الطين المعدني لمدينة سدراتة', 'price': 1200, 
             'desc': 'يُستخرج من طبيعة مناطق سدراتة الخلابة. ينظف البشرة بلطف بعيداً عن المواد الكيميائية.'},
            
            # منتجات إضافية
             {'vendor': vendors[0], 'cat': cat_skincare, 'name': 'كريم العناية بالبشرة وحب الشباب', 'price': 1500, 
             'desc': 'تركيبة سويسرية معبأة في الجزائر.'},
        ]

        demo_product_images = [
            'demo/products/76843.jpeg',
            'demo/products/43f62bee7e196db9cfddf48ff11bc404.jpg',
            'demo/products/2D75cWvMYYIYBLLKb4dzTKMzzfYVqKOtgIsysRwX.jpg',
            'demo/products/7850893a-486d-488a-89ba-a7c2fb1564af-1000x562-FgLIOPE8lZWEh8zTwnbhoaVg2qEvSrQ9ez3cb1qz.webp',
            'demo/products/أفضل-منتجات-طبيعية-للعناية-بالبشرة-كريم-عناية-بالبشرة.jpg',
        ]

        for i, p in enumerate(products_config):
            # ربط الصورة
            img_source = demo_product_images[i % len(demo_product_images)]
            slug = slugify(p['name'], allow_unicode=True) or f"product-{i}"
            ext = os.path.splitext(img_source)[1]
            dest_relative = f'products/{slug}/main{ext}'
            dest_full = os.path.join(settings.MEDIA_ROOT, dest_relative)
            os.makedirs(os.path.dirname(dest_full), exist_ok=True)
            source_full = os.path.join(settings.MEDIA_ROOT, img_source)
            if os.path.exists(source_full):
                shutil.copy2(source_full, dest_full)

            Product.objects.create(
                vendor=p['vendor'],
                category=p['cat'],
                name=p['name'],
                description=p['desc'],
                price=Decimal(str(p['price'])),
                stock=random.randint(10, 50),
                is_active=True,
                is_featured=True,
                image_main=dest_relative if os.path.exists(source_full) else None,
            )

        # ═══════════════════════════════════════════════════════════
        # 7. التقييمات
        # ═══════════════════════════════════════════════════════════
        for items in [Product.objects.all(), Service.objects.all()]:
            for item in items:
                Review.objects.create(
                    user=customers[0],
                    product=item if isinstance(item, Product) else None,
                    service=item if isinstance(item, Service) else None,
                    rating=5,
                    comment='خدمة رائعة جدا وفي المستوى المأمول.'
                )

        self.stdout.write(self.style.SUCCESS(
            "\n=== DATABASE POPULATED SUCCESSFULLY ==="
            "\n  Products:  6"
            "\n  Services:  6"
            "\n=================================\n"
        ))
