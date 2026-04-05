import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.users.models import User
from apps.products.models import Product, Category
from apps.services.models import Service, ServiceCategory
from apps.orders.models import Order
from apps.reviews.models import Review


class Command(BaseCommand):
    help = 'تعبئة قاعدة البيانات بمنتجات وخدمات حقيقية من السوق الجزائرية مع التركيز على القطاع الصحي'

    def handle(self, *args, **kwargs):
        self.stdout.write("[CLEAN] Cleaning old test data...")
        Review.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Service.objects.all().delete()
        Category.objects.all().delete()
        ServiceCategory.objects.all().delete()
        User.objects.filter(is_staff=False).delete()

        # ═══════════════════════════════════════════════════════════
        # 1. إنشاء المستخدمين
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[USERS] Creating accounts...")

        admin, _ = User.objects.get_or_create(username='admin_sivar', is_staff=True, is_superuser=True)
        admin.set_password('Sivar2024!')
        admin.save()

        inc, _ = User.objects.get_or_create(
            username='incubator_dz', role='INCUBATOR',
            first_name='حاضنة الأعمال الجزائرية', phone_number='0550112233'
        )
        inc.set_password('Sivar2024!')
        inc.save()

        inst_medical, _ = User.objects.get_or_create(
            username='clinique_el_azhar', role='INSTITUTION',
            first_name='مصحة الأزهر للجراحة', incubator=inc, phone_number='0550112244'
        )
        inst_medical.is_verified = True
        inst_medical.performance_score = 92
        inst_medical.set_password('Sivar2024!')
        inst_medical.save()

        inst_tourism, _ = User.objects.get_or_create(
            username='siha_travel', role='INSTITUTION',
            first_name='صحة ترافل للسياحة العلاجية', incubator=inc, phone_number='0550112255'
        )
        inst_tourism.is_verified = True
        inst_tourism.performance_score = 88
        inst_tourism.set_password('Sivar2024!')
        inst_tourism.save()

        inst_pharma, _ = User.objects.get_or_create(
            username='pharma_plus_dz', role='INSTITUTION',
            first_name='فارما بلس الجزائر', incubator=None, phone_number='0550112266'
        )
        inst_pharma.is_verified = True
        inst_pharma.performance_score = 90
        inst_pharma.set_password('Sivar2024!')
        inst_pharma.save()

        vendor_health, _ = User.objects.get_or_create(
            username='davapharm', role='SELLER',
            first_name='دافا فارم للأجهزة الطبية', phone_number='0550112277'
        )
        vendor_health.set_password('Sivar2024!')
        vendor_health.save()

        vendor_beauty, _ = User.objects.get_or_create(
            username='beaute_naturelle', role='SELLER',
            first_name='جمال طبيعي - مستحضرات', phone_number='0550112288'
        )
        vendor_beauty.set_password('Sivar2024!')
        vendor_beauty.save()

        vendor_tech, _ = User.objects.get_or_create(
            username='techno_medical', role='SELLER',
            first_name='تكنو ميديكال', phone_number='0550112299'
        )
        vendor_tech.set_password('Sivar2024!')
        vendor_tech.save()

        customers = []
        customer_names = ['أحمد بن علي', 'فاطمة الزهراء', 'يوسف خالدي', 'مريم بوعلام', 'كريم حدادي']
        for i, name in enumerate(customer_names):
            c, _ = User.objects.get_or_create(
                username=f'customer_{i}', role='CUSTOMER',
                first_name=name, phone_number=f'066011227{i}'
            )
            c.set_password('Sivar2024!')
            c.save()
            customers.append(c)

        # ═══════════════════════════════════════════════════════════
        # 2. تصنيفات المنتجات (هرمية)
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[CATS] Creating product categories...")

        # تصنيفات رئيسية
        cat_health = Category.objects.create(name='المنتجات الصحية والطبية', slug='health-medical-products')
        cat_beauty = Category.objects.create(name='العناية والتجميل', slug='beauty-care')
        cat_nutrition = Category.objects.create(name='التغذية والمكملات', slug='nutrition-supplements')
        cat_equipment = Category.objects.create(name='الأجهزة والمعدات الطبية', slug='medical-equipment')
        cat_baby = Category.objects.create(name='الأم والطفل', slug='mother-baby')
        cat_sports = Category.objects.create(name='الرياضة واللياقة', slug='sports-fitness')

        # تصنيفات فرعية للمنتجات الصحية
        cat_firstaid = Category.objects.create(name='الإسعافات الأولية', slug='first-aid', parent=cat_health)
        cat_monitoring = Category.objects.create(name='أجهزة القياس والمراقبة', slug='health-monitoring', parent=cat_health)
        cat_ortho = Category.objects.create(name='مستلزمات العظام والمفاصل', slug='orthopedic', parent=cat_health)
        cat_respiratory = Category.objects.create(name='أجهزة التنفس', slug='respiratory', parent=cat_health)

        # ═══════════════════════════════════════════════════════════
        # 3. تصنيفات الخدمات
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[CATS] Creating service categories...")

        scat_medical_tourism = ServiceCategory.objects.create(name='السياحة العلاجية', slug='medical-tourism')
        scat_health_services = ServiceCategory.objects.create(name='الخدمات الصحية المنزلية', slug='home-health-services')
        scat_dental = ServiceCategory.objects.create(name='طب الأسنان', slug='dental-services')
        scat_ophthalmology = ServiceCategory.objects.create(name='طب العيون والليزر', slug='ophthalmology')
        scat_rehabilitation = ServiceCategory.objects.create(name='العلاج الطبيعي والتأهيل', slug='rehabilitation')
        scat_aesthetics = ServiceCategory.objects.create(name='التجميل والعمليات التجميلية', slug='aesthetic-surgery')
        scat_laboratory = ServiceCategory.objects.create(name='التحاليل والفحوصات المخبرية', slug='laboratory-tests')
        scat_consulting = ServiceCategory.objects.create(name='الاستشارات الطبية', slug='medical-consulting')

        # ═══════════════════════════════════════════════════════════
        # 4. المنتجات الحقيقية
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[PRODUCTS] Creating products...")

        products_data = [
            # ── المنتجات الصحية والطبية ──
            {'name': 'جهاز قياس ضغط الدم الرقمي Omron M3', 'cat': cat_monitoring, 'vendor': vendor_health, 'price': 8500, 'brand': 'Omron', 'desc': 'جهاز قياس ضغط الدم الأوتوماتيكي بتقنية IntelliSense للقياس الدقيق. شاشة LCD كبيرة مع ذاكرة 60 قراءة. مناسب للاستخدام المنزلي اليومي.'},
            {'name': 'جهاز قياس السكر في الدم Accu-Chek Active', 'cat': cat_monitoring, 'vendor': vendor_health, 'price': 4200, 'brand': 'Roche', 'desc': 'جهاز فحص السكري بتقنية الشريط المتقدمة. نتائج في 5 ثوانٍ مع ذاكرة 500 قراءة. يتضمن 10 شرائط فحص وإبر وخز.'},
            {'name': 'ميزان حرارة رقمي بالأشعة تحت الحمراء', 'cat': cat_monitoring, 'vendor': vendor_tech, 'price': 3800, 'brand': 'Braun', 'desc': 'ميزان حرارة إلكتروني لا تلامسي. قياس فوري من الجبهة في ثانية واحدة. آمن للأطفال ومناسب لجميع أفراد العائلة.'},
            {'name': 'جهاز قياس نبضات القلب ونسبة الأكسجين (Pulse Oximeter)', 'cat': cat_monitoring, 'vendor': vendor_health, 'price': 2500, 'brand': 'Beurer', 'desc': 'جهاز أصبعي لقياس SpO2 ونبض القلب لحظياً. شاشة OLED ملونة. خفيف الوزن ومثالي للاستخدام المنزلي.'},
            {'name': 'حقيبة إسعافات أولية متكاملة 180 قطعة', 'cat': cat_firstaid, 'vendor': vendor_health, 'price': 5500, 'brand': 'First Aid Kit Pro', 'desc': 'حقيبة طبية شاملة للطوارئ تحتوي على 180 قطعة: ضمادات، شاش، مطهرات، مقص طبي، قفازات. مناسبة للمنزل والسيارة والرحلات.'},
            {'name': 'مشد ظهر طبي لتصحيح القوام', 'cat': cat_ortho, 'vendor': vendor_tech, 'price': 3200, 'brand': 'Dr. Back', 'desc': 'مشد ظهر قابل للتعديل لتصحيح وضعية الجلوس والوقوف. مصنوع من قماش قابل للتنفس. يخفف آلام أسفل الظهر والكتفين.'},
            {'name': 'كرسي متحرك خفيف قابل للطي', 'cat': cat_ortho, 'vendor': inst_pharma, 'price': 35000, 'brand': 'Breezy', 'desc': 'كرسي متحرك يدوي خفيف الوزن (11 كجم) مصنوع من الألمنيوم. قابل للطي بسهولة للتنقل والسفر. مقعد مبطن مريح.'},
            {'name': 'جهاز بخاخ طبي (نبيوليزر) للأطفال والكبار', 'cat': cat_respiratory, 'vendor': vendor_health, 'price': 6800, 'brand': 'Omron', 'desc': 'جهاز استنشاق كهربائي لعلاج الربو وأمراض الجهاز التنفسي. يعمل بتقنية الضغط الهوائي. هادئ الصوت ومناسب للأطفال.'},
            {'name': 'جهاز تركيز الأكسجين المحمول 5 لتر', 'cat': cat_respiratory, 'vendor': inst_pharma, 'price': 82000, 'brand': 'Philips', 'desc': 'جهاز أكسجين طبي منزلي بتدفق 5 لتر/دقيقة. مثالي للمرضى الذين يعانون من صعوبات تنفسية مزمنة. تشغيل مستمر 24 ساعة.'},
            {'name': 'وسادة طبية لعلاج آلام الرقبة', 'cat': cat_ortho, 'vendor': vendor_tech, 'price': 4500, 'brand': 'Tempur', 'desc': 'وسادة ميموري فوم تشريحية لدعم الرقبة أثناء النوم. تخفف التوتر العضلي وتحسن جودة النوم. غلاف قابل للغسل.'},

            # ── العناية والتجميل ──
            {'name': 'زيت الأركان المغربي الأصلي 100 مل', 'cat': cat_beauty, 'vendor': vendor_beauty, 'price': 2800, 'brand': 'Bio Argan', 'desc': 'زيت أركان عضوي مستخلص بالضغط البارد. مرطب عميق للبشرة والشعر. غني بفيتامين E ومضادات الأكسدة. منتج طبيعي 100%.'},
            {'name': 'كريم الحلزون لتجديد البشرة', 'cat': cat_beauty, 'vendor': vendor_beauty, 'price': 3500, 'brand': 'Snail White', 'desc': 'كريم مرطب بمستخلص الحلزون الطبيعي لتجديد خلايا البشرة. يقلل التجاعيد والبقع الداكنة. مناسب لجميع أنواع البشرة.'},
            {'name': 'ماء الورد الطبيعي للبشرة 250 مل', 'cat': cat_beauty, 'vendor': vendor_beauty, 'price': 1200, 'brand': 'Roses de Blida', 'desc': 'ماء ورد طبيعي من ورود البليدة الجزائرية. تونر منعش ومنقي للبشرة. خالي من المواد الكيميائية والكحول.'},
            {'name': 'صابون طبيعي بزيت الزيتون والغار', 'cat': cat_beauty, 'vendor': vendor_beauty, 'price': 800, 'brand': 'Savon d\'Alep', 'desc': 'صابون حلبي تقليدي بزيت الزيتون وزيت الغار. مناسب للبشرة الحساسة والأكزيما. صناعة يدوية تقليدية.'},
            {'name': 'زيت الحبة السوداء البكر 250 مل', 'cat': cat_beauty, 'vendor': vendor_beauty, 'price': 2200, 'brand': 'Nigelle Premium', 'desc': 'زيت الحبة السوداء النقي المعصور على البارد. يقوي جهاز المناعة ويعالج مشاكل البشرة. منتج جزائري طبيعي 100%.'},

            # ── التغذية والمكملات ──
            {'name': 'عسل السدر الجبلي الجزائري 500 غ', 'cat': cat_nutrition, 'vendor': vendor_beauty, 'price': 6000, 'brand': 'Miel Pur', 'desc': 'عسل سدر طبيعي من جبال الأوراس. غني بالمعادن ومقوي للمناعة. إنتاج محلي بدون معالجة حرارية.'},
            {'name': 'مكمل فيتامين D3 2000 وحدة دولية', 'cat': cat_nutrition, 'vendor': inst_pharma, 'price': 1800, 'brand': 'Saidal', 'desc': 'كبسولات فيتامين D3 لتعويض النقص ودعم صحة العظام والمناعة. إنتاج مجمع صيدال الجزائري. عبوة 60 كبسولة.'},
            {'name': 'بروتين مصل اللبن (Whey Protein) فانيلا 1 كجم', 'cat': cat_nutrition, 'vendor': vendor_tech, 'price': 7500, 'brand': 'Gold Standard', 'desc': 'مسحوق بروتين عالي الجودة لبناء العضلات. 24 غرام بروتين لكل حصة. مناسب للرياضيين وعشاق اللياقة البدنية.'},
            {'name': 'حبوب أوميغا 3 زيت السمك 1000 مغ', 'cat': cat_nutrition, 'vendor': inst_pharma, 'price': 2500, 'brand': 'Biopharm', 'desc': 'كبسولات أوميغا 3 لصحة القلب والدماغ والمفاصل. تركيز عالي من EPA و DHA. عبوة 90 كبسولة.'},
            {'name': 'شاي الأعشاب المهدئ - مزيج جزائري', 'cat': cat_nutrition, 'vendor': vendor_beauty, 'price': 950, 'brand': 'Tisane DZ', 'desc': 'خلطة أعشاب طبيعية من البابونج والنعناع وإكليل الجبل. تساعد على الاسترخاء وتحسين الهضم. 20 كيس فلتر.'},

            # ── الأجهزة والمعدات الطبية ──
            {'name': 'سماعة طبيب (ستيثوسكوب) Littmann Classic III', 'cat': cat_equipment, 'vendor': vendor_health, 'price': 12000, 'brand': '3M Littmann', 'desc': 'سماعة طبية احترافية ذات أداء صوتي عالٍ. مناسبة للفحص العام للقلب والرئتين. تصميم خفيف ومريح.'},
            {'name': 'جهاز ضغط يدوي (أنيرويد) للمحترفين', 'cat': cat_equipment, 'vendor': vendor_health, 'price': 4500, 'brand': 'Riester', 'desc': 'جهاز قياس ضغط الدم الزئبقي اليدوي للاستخدام المهني. دقة عالية مع كفة قابلة للتعديل. مثالي للعيادات والصيدليات.'},
            {'name': 'سرير فحص طبي كهربائي', 'cat': cat_equipment, 'vendor': inst_pharma, 'price': 95000, 'brand': 'Promotal', 'desc': 'سرير فحص كهربائي بثلاث محركات. ارتفاع قابل للتعديل وظهر قابل للإمالة. مع ورق فحص ومسند رأس.'},
            {'name': 'جهاز تعقيم بالأشعة فوق البنفسجية', 'cat': cat_equipment, 'vendor': vendor_tech, 'price': 8500, 'brand': 'UV Clean Pro', 'desc': 'جهاز تعقيم لأدوات الطبيب وأسطح الأجهزة. يقتل 99.9% من الجراثيم في دقائق. تصميم محمول وسهل الاستخدام.'},

            # ── الأم والطفل ──
            {'name': 'شفاط حليب كهربائي صامت', 'cat': cat_baby, 'vendor': vendor_tech, 'price': 6500, 'brand': 'Medela', 'desc': 'شفاط حليب إلكتروني مزدوج بتقنية الشفط الطبيعي. خفيف وقابل للتنقل. مع زجاجات تخزين وأكياس حفظ.'},
            {'name': 'ميزان رقمي لوزن الرضّع', 'cat': cat_baby, 'vendor': vendor_health, 'price': 5200, 'brand': 'Beurer', 'desc': 'ميزان إلكتروني دقيق لمتابعة نمو الطفل. سطح مريح وآمن للرضيع. ذاكرة لتتبع الوزن مع مرور الوقت.'},
            {'name': 'حاملة أطفال طبية لدعم الظهر', 'cat': cat_baby, 'vendor': vendor_beauty, 'price': 4800, 'brand': 'Ergobaby', 'desc': 'حاملة أطفال مريحة بتصميم طبي يدعم ظهر الطفل والأم. لعمر 0-36 شهر. قابلة للتعديل ومصنوعة من قماش عضوي.'},

            # ── الرياضة واللياقة ──
            {'name': 'حبل مقاومة مرن للتمارين المنزلية (مجموعة 5)', 'cat': cat_sports, 'vendor': vendor_tech, 'price': 3500, 'brand': 'FitBand', 'desc': 'مجموعة 5 أحبال مقاومة بمستويات شد مختلفة. مناسبة لتمارين إعادة التأهيل واللياقة. مع دليل تمارين مجاني.'},
            {'name': 'ساعة ذكية لمراقبة الصحة واللياقة', 'cat': cat_sports, 'vendor': vendor_tech, 'price': 9500, 'brand': 'Xiaomi Band', 'desc': 'ساعة ذكية بمستشعر نبض القلب وأكسجين الدم. مقاومة للماء مع تتبع النوم والنشاط. بطارية تدوم 14 يوماً.'},
            {'name': 'حذاء مشي طبي لمرضى السكري', 'cat': cat_sports, 'vendor': vendor_health, 'price': 8500, 'brand': 'Dr. Comfort', 'desc': 'حذاء طبي مصمم خصيصاً لمرضى السكر والقدم الحساسة. نعل طبي داعم لتفادي التقرحات. متوفر بعدة مقاسات.'},
        ]

        for i, p in enumerate(products_data):
            discount = None
            if random.random() < 0.3:
                discount = Decimal(str(round(p['price'] * random.uniform(0.7, 0.9), -1)))

            Product.objects.create(
                vendor=p['vendor'],
                category=p['cat'],
                name=p['name'],
                description=p['desc'],
                brand=p.get('brand', ''),
                price=Decimal(str(p['price'])),
                discount_price=discount,
                stock=random.randint(5, 150),
                is_active=True,
                is_featured=random.random() < 0.25,
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(products_data)} products"))

        # ═══════════════════════════════════════════════════════════
        # 5. الخدمات الحقيقية
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[SERVICES] Creating services...")

        services_data = [
            # ── السياحة العلاجية ──
            {'name': 'برنامج زراعة الشعر بتقنية FUE في إسطنبول', 'cat': scat_medical_tourism, 'vendor': inst_tourism, 'price': 350000,
             'desc': 'برنامج متكامل يشمل: تذاكر الطيران، الإقامة الفندقية 5 نجوم، النقل، العملية الجراحية بأحدث تقنية FUE، ومتابعة ما بعد العملية لمدة عام.'},
            {'name': 'جراحة السمنة (تكميم المعدة) في تركيا', 'cat': scat_medical_tourism, 'vendor': inst_tourism, 'price': 480000,
             'desc': 'عملية تكميم المعدة بالمنظار في أهم مستشفيات إسطنبول. يشمل الإقامة، التحاليل، الجراحة، والمتابعة الغذائية لمدة 6 أشهر.'},
            {'name': 'العلاج بالمياه المعدنية - حمام الصالحين (بسكرة)', 'cat': scat_medical_tourism, 'vendor': inst_tourism, 'price': 45000,
             'desc': 'برنامج علاجي لمدة أسبوع في حمام الصالحين ببسكرة. حمامات مياه معدنية ساخنة لعلاج الروماتيزم وأمراض المفاصل. مع إقامة وتغذية كاملة.'},
            {'name': 'رحلة علاجية لمنتجعات حمام بوحنيفية (معسكر)', 'cat': scat_medical_tourism, 'vendor': inst_tourism, 'price': 55000,
             'desc': 'برنامج 10 أيام في منتجع حمام بوحنيفية العلاجي. جلسات علاجية بمياه حرارية طبيعية لأمراض الجلد والعظام. إقامة فندقية وتغذية شاملة.'},
            {'name': 'تنسيق رحلة علاج العقم في ألمانيا', 'cat': scat_medical_tourism, 'vendor': inst_tourism, 'price': 650000,
             'desc': 'برنامج شامل لعلاج تأخر الإنجاب في أرقى مراكز الخصوبة الألمانية. يشمل الفحوصات، العلاج بتقنية IVF، الإقامة، والترجمة.'},
            {'name': 'علاج بالمياه المعدنية - حمام ملوان (البليدة)', 'cat': scat_medical_tourism, 'vendor': inst_tourism, 'price': 38000,
             'desc': 'برنامج استشفائي في حمام ملوان الشهير بالبليدة. مياه معدنية طبيعية لعلاج أمراض الكلى والمسالك البولية. إقامة 7 أيام.'},
            {'name': 'جراحة العمود الفقري بالتنظير في المصحة الكبرى', 'cat': scat_medical_tourism, 'vendor': inst_medical, 'price': 420000,
             'desc': 'عملية الانزلاق الغضروفي بتقنية المنظار المتطورة. إقامة في مصحة مجهزة مع متابعة طبية متخصصة بعد العملية.'},

            # ── الخدمات الصحية المنزلية ──
            {'name': 'تمريض منزلي 24/24 ساعة', 'cat': scat_health_services, 'vendor': inst_medical, 'price': 8000,
             'desc': 'خدمة تمريض منزلي على مدار الساعة. ممرضون مؤهلون لرعاية المسنين وما بعد العمليات. متابعة الأدوية وقياسات الضغط والسكر.'},
            {'name': 'تحاليل مخبرية منزلية (سحب دم + نتائج)', 'cat': scat_health_services, 'vendor': inst_medical, 'price': 3500,
             'desc': 'خدمة سحب عينات الدم في المنزل مع توصيل النتائج خلال 24 ساعة. تشمل: فحص الدم الشامل، السكر، الكولسترول، الكلى، الكبد.'},
            {'name': 'نقل إسعافي خاص مجهز', 'cat': scat_health_services, 'vendor': inst_medical, 'price': 5000,
             'desc': 'خدمة نقل بسيارة إسعاف مجهزة بالكامل مع ممرض مرافق. متوفرة على مدار الساعة في ولاية الجزائر وضواحيها.'},
            {'name': 'رعاية مسنين منزلية - باقة أسبوعية', 'cat': scat_health_services, 'vendor': inst_medical, 'price': 25000,
             'desc': 'خدمة رعاية شاملة للمسنين في المنزل: مراقبة طبية، تغذية، نظافة شخصية، مرافقة للأطباء. طاقم مؤهل ومدرب.'},
            {'name': 'جلسة حجامة علاجية في المنزل', 'cat': scat_health_services, 'vendor': vendor_health, 'price': 4000,
             'desc': 'جلسة حجامة وفق الأصول الطبية على يد متخصصين مؤهلين. تشمل الأدوات المعقمة والاستشارة. خدمة منزلية آمنة ومريحة.'},

            # ── طب الأسنان ──
            {'name': 'تبييض الأسنان بتقنية Zoom الاحترافية', 'cat': scat_dental, 'vendor': inst_pharma, 'price': 15000,
             'desc': 'جلسة تبييض أسنان بالليزر في العيادة. نتائج فورية تصل لـ 8 درجات أفتح خلال ساعة واحدة. آمن على المينا.'},
            {'name': 'زراعة سن واحد (Implant) تيتانيوم', 'cat': scat_dental, 'vendor': inst_pharma, 'price': 60000,
             'desc': 'زراعة سنية بغرسة تيتانيوم سويسرية مع تاج بورسلان. يتضمن الفحص بالأشعة ثلاثية الأبعاد والجراحة والمتابعة.'},
            {'name': 'تقويم أسنان شفاف (Invisalign)', 'cat': scat_dental, 'vendor': inst_pharma, 'price': 180000,
             'desc': 'تقويم أسنان غير مرئي بالقوالب الشفافة. خطة علاج رقمية مخصصة مع متابعة شهرية. مدة العلاج 12-18 شهر.'},

            # ── طب العيون والليزر ──
            {'name': 'عملية تصحيح النظر بالليزك (LASIK)', 'cat': scat_ophthalmology, 'vendor': inst_medical, 'price': 85000,
             'desc': 'عملية تصحيح النظر بتقنية LASIK لعلاج قصر وطول النظر والاستجماتيزم. فحص شامل مسبق مع متابعة لمدة 6 أشهر.'},
            {'name': 'عملية إزالة المياه البيضاء (الساد)', 'cat': scat_ophthalmology, 'vendor': inst_medical, 'price': 65000,
             'desc': 'عملية استخراج المياه البيضاء وزرع عدسة متعددة البؤر. جراحة بالموجات فوق الصوتية (Phaco). نتائج فورية ومضمونة.'},
            {'name': 'فحص عيون شامل + قياس النظر المحوسب', 'cat': scat_ophthalmology, 'vendor': inst_medical, 'price': 3500,
             'desc': 'فحص عيون كامل يشمل: قياس حدة البصر، فحص قاع العين، قياس ضغط العين، OCT. مع وصفة نظارات أو عدسات.'},

            # ── العلاج الطبيعي والتأهيل ──
            {'name': 'جلسة علاج طبيعي وإعادة تأهيل', 'cat': scat_rehabilitation, 'vendor': inst_medical, 'price': 3500,
             'desc': 'جلسة علاج طبيعي فردية على يد أخصائي مؤهل. تشمل تمارين تقوية، تحريك المفاصل، والعلاج بالتيارات الكهربائية.'},
            {'name': 'برنامج تأهيل ما بعد عمليات الركبة (10 جلسات)', 'cat': scat_rehabilitation, 'vendor': inst_medical, 'price': 30000,
             'desc': 'برنامج متكامل لاستعادة الحركة بعد جراحة الركبة. 10 جلسات مع أخصائي علاج طبيعي. تمارين مقاومة + علاج مائي.'},
            {'name': 'جلسة راحة وتدليك علاجي سويدي', 'cat': scat_rehabilitation, 'vendor': vendor_beauty, 'price': 5000,
             'desc': 'جلسة تدليك علاجية لتخفيف التوتر وآلام العضلات. 60 دقيقة على يد معالج مختص. مع زيوت عطرية طبيعية.'},

            # ── التجميل والعمليات التجميلية ──
            {'name': 'حقن البوتوكس لإزالة التجاعيد', 'cat': scat_aesthetics, 'vendor': inst_pharma, 'price': 25000,
             'desc': 'حقن بوتوكس أمريكي (Allergan) لتقليل تجاعيد الجبهة وحول العينين. إجراء سريع بدون تخدير عام. نتائج فورية.'},
            {'name': 'جلسة ليزر لإزالة الشعر - منطقة كاملة', 'cat': scat_aesthetics, 'vendor': inst_pharma, 'price': 8000,
             'desc': 'جلسة إزالة شعر بتقنية ليزر ديود الأخيرة. مناسبة لجميع أنواع وألوان البشرة. نتائج دائمة بعد 6-8 جلسات.'},
            {'name': 'جلسة تنظيف بشرة عميق بالهيدرافيشل', 'cat': scat_aesthetics, 'vendor': vendor_beauty, 'price': 6000,
             'desc': 'جلسة تنظيف عميق للبشرة بجهاز HydraFacial. تقشير، استخراج رؤوس سوداء، ترطيب بمصل مغذي. نتائج فورية ومشرقة.'},

            # ── التحاليل والفحوصات المخبرية ──
            {'name': 'فحص طبي شامل (Check-up) أساسي', 'cat': scat_laboratory, 'vendor': inst_medical, 'price': 12000,
             'desc': 'فحص طبي شامل يتضمن: تحاليل الدم الشاملة، وظائف الكلى والكبد، السكر، الدهنيات، البول، ECG. مع تقرير طبي مفصل.'},
            {'name': 'تحليل الحساسية الغذائية (IgE Panel)', 'cat': scat_laboratory, 'vendor': inst_medical, 'price': 8500,
             'desc': 'تحليل شامل للحساسية الغذائية لـ 200 مادة غذائية. عينة دم بسيطة مع نتائج تفصيلية وتوصيات غذائية.'},
            {'name': 'فحص هرمونات شامل للمرأة', 'cat': scat_laboratory, 'vendor': inst_medical, 'price': 7000,
             'desc': 'تحاليل هرمونية شاملة: FSH, LH, Estradiol, Progesterone, TSH, Prolactin. مثالي لمتابعة الخصوبة والدورة الشهرية.'},

            # ── الاستشارات الطبية ──
            {'name': 'استشارة طبية عن بُعد (تيليميديسين)', 'cat': scat_consulting, 'vendor': inst_medical, 'price': 2500,
             'desc': 'استشارة طبية بالفيديو مع طبيب مختص. مدة الجلسة 30 دقيقة. تشمل وصفة طبية إلكترونية إذا لزم الأمر.'},
            {'name': 'استشارة تغذية علاجية مع برنامج غذائي', 'cat': scat_consulting, 'vendor': inst_pharma, 'price': 4500,
             'desc': 'جلسة استشارة مع أخصائي تغذية معتمد. إعداد برنامج غذائي مخصص حسب الحالة الصحية مع متابعة شهرية.'},
            {'name': 'استشارة نفسية متخصصة (جلسة فردية)', 'cat': scat_consulting, 'vendor': inst_medical, 'price': 5000,
             'desc': 'جلسة علاج نفسي فردية مع أخصائي نفساني معتمد. 50 دقيقة. سرية تامة. مناسبة للقلق، الاكتئاب، والضغوط النفسية.'},
        ]

        for i, s in enumerate(services_data):
            Service.objects.create(
                vendor=s['vendor'],
                category=s['cat'],
                name=s['name'],
                description=s['desc'],
                price=Decimal(str(s['price'])),
                is_active=True,
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(services_data)} services"))

        # ═══════════════════════════════════════════════════════════
        # 6. تقييمات واقعية
        # ═══════════════════════════════════════════════════════════
        self.stdout.write("[REVIEWS] Adding reviews...")

        review_comments = [
            "تجربة ممتازة، أنصح بشدة 👍",
            "خدمة احترافية عالية الجودة",
            "السعر مناسب جداً مقارنة بالمنافسين",
            "التوصيل سريع والتغليف ممتاز",
            "جودة عالية وخدمة ما بعد البيع ممتازة",
            "منتج/خدمة تستحق كل ريال",
            "النتائج كانت مبهرة فعلاً",
            "فريق محترف ومتعاون",
            "سأتعامل معهم مرة أخرى بالتأكيد",
            "أفضل تجربة شراء أونلاين في الجزائر",
        ]

        all_products = list(Product.objects.all())
        all_services = list(Service.objects.all())
        all_items = all_products + all_services

        for item in all_items:
            num_reviews = random.randint(2, 5)
            reviewers = random.sample(customers, k=min(num_reviews, len(customers)))
            for reviewer in reviewers:
                Review.objects.create(
                    user=reviewer,
                    product=item if isinstance(item, Product) else None,
                    service=item if isinstance(item, Service) else None,
                    rating=random.choice([4, 4, 5, 5, 5]),
                    comment=random.choice(review_comments),
                )

        total_reviews = Review.objects.count()
        self.stdout.write(self.style.SUCCESS(f"[OK] Created {total_reviews} reviews"))

        # ═══════════════════════════════════════════════════════════
        # 7. ملخص نهائي
        # ═══════════════════════════════════════════════════════════
        self.stdout.write(self.style.SUCCESS(
            f"\n=== DATABASE POPULATED SUCCESSFULLY ==="
            f"\n  Products:  {Product.objects.count()}"
            f"\n  Services:  {Service.objects.count()}"
            f"\n  Product Categories: {Category.objects.count()}"
            f"\n  Service Categories: {ServiceCategory.objects.count()}"
            f"\n  Reviews: {total_reviews}"
            f"\n  Users: {User.objects.count()}"
            f"\n\n  Login Accounts:"
            f"\n  admin_sivar / Sivar2024!"
            f"\n  clinique_el_azhar / Sivar2024! (institution)"
            f"\n  siha_travel / Sivar2024! (medical tourism)"
            f"\n  pharma_plus_dz / Sivar2024! (pharma)"
            f"\n  davapharm / Sivar2024! (vendor)"
            f"\n  beaute_naturelle / Sivar2024! (vendor)"
            f"\n  customer_0 / Sivar2024! (customer)"
            f"\n  incubator_dz / Sivar2024! (incubator)"
            f"\n=================================\n"
        ))
