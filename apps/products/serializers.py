"""
Serializers لتطبيق المنتجات.

الملف: apps/products/serializers.py

الهيكل:
    CategorySerializer              → عرض بسيط للتصنيف (للقراءة والـ Nested)
    ProductImageSerializer          → عرض صور المنتج الإضافية
    ProductSerializer               → عرض كامل للمنتج  (للقراءة)
    ProductCreateUpdateSerializer   → إنشاء وتعديل المنتج (للكتابة)

نمط الفصل بين Read/Write Serializers:
    ✔ Read  Serializer → بيانات ثرية ومتداخلة (Nested)، لا تقبل مدخلات.
    ✔ Write Serializer → يقبل IDs بسيطة، يتحقق من صحة البيانات، يُرجع Read Serializer.
"""

from rest_framework import serializers

from .models import Category, Product, ProductImage


# ══════════════════════════════════════════════════════════════════════════════
# 1. CategorySerializer — التصنيف (Read + Nested)
# ══════════════════════════════════════════════════════════════════════════════

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer بسيط لعرض بيانات التصنيف.

    الاستخدامات:
        - كـ Endpoint مستقل في CategoryViewSet.
        - كـ Nested Serializer داخل ProductSerializer.
        - مطلوب search_fields في CategoryAdmin لدعم autocomplete_fields.
    """
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'parent_name']

    def get_parent_name(self, obj):
        """يُرجع اسم التصنيف الأب إن وُجد."""
        if obj.parent:
            return obj.parent.name
        return None


# ══════════════════════════════════════════════════════════════════════════════
# 1.5 ProductImageSerializer — صور المنتج الإضافية
# ══════════════════════════════════════════════════════════════════════════════

class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer لعرض الصور الإضافية للمنتج.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'order']
        read_only_fields = ['id', 'image_url']

    def get_image_url(self, obj: ProductImage) -> str | None:
        """يُرجع الرابط الكامل للصورة."""
        if not obj.image:
            return None
        request = self.context.get('request')
        url = obj.image.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url


# ══════════════════════════════════════════════════════════════════════════════
# 2. ProductSerializer — عرض المنتج الكامل (Read Only)
# ══════════════════════════════════════════════════════════════════════════════

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer كامل لعرض بيانات المنتج (عمليات القراءة: GET / LIST / RETRIEVE).

    الحقول المحسوبة (SerializerMethodField):
        vendor_name         → اسم البائع الكامل  (أو username كاحتياط)
        is_in_stock         → هل المخزون متوفر؟   (stock > 0)
        final_price         → السعر النهائي بعد الخصم
        discount_percentage → نسبة الخصم كعدد صحيح (0 إذا لا يوجد خصم)
        image_main          → Absolute URL للصورة الرئيسية

    الحقول المتداخلة (Nested):
        category            → كائن {id, name, slug} بدلاً من مجرد رقم ID
        images              → قائمة بالصور الإضافية للمنتج
    """

    # ── Nested Serializer ──────────────────────────────────────────────────────
    # read_only=True: لا يقبل مدخلات من المستخدم — للعرض فقط.
    category = CategorySerializer(read_only=True)
    images   = ProductImageSerializer(many=True, read_only=True)

    # ── Computed Fields ────────────────────────────────────────────────────────
    # SerializerMethodField → يستدعي get_<field_name>(self, obj) تلقائياً.
    vendor_name         = serializers.SerializerMethodField()
    is_in_stock         = serializers.SerializerMethodField()
    final_price         = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    image_main          = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            # ── التعريف ───────────────────────────────────
            'id',
            'name',
            'slug',
            'description',
            # ── العلاقات ──────────────────────────────────
            'category',            # Nested object {id, name, slug}
            'vendor',              # FK ID (للمرجعية التقنية)
            'vendor_name',         # computed: اسم البائع
            # ── التسعير ───────────────────────────────────
            'price',               # السعر الأصلي
            'discount_price',      # سعر الخصم (nullable)
            'final_price',         # computed: السعر النهائي
            'discount_percentage', # computed: نسبة التوفير %
            # ── المخزون ───────────────────────────────────
            'stock',               # الكمية المتاحة
            'is_in_stock',         # computed: توفر المخزون
            # ── الوسائط ───────────────────────────────────
            'image_main',          # computed: Absolute URL
            'images',              # Nested objects: صور إضافية
            # ── الحالة ────────────────────────────────────
            'is_active',
            'is_featured',
            # ── التواريخ ──────────────────────────────────
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'vendor', 'created_at', 'updated_at']

    # ══════════════════════════════════════════════════════════════════════════
    # get_* Methods — منطق الحقول المحسوبة
    # ══════════════════════════════════════════════════════════════════════════

    def get_vendor_name(self, obj: Product) -> str:
        """
        يُرجع الاسم الكامل للبائع (التاجر).

        المنطق:
            1. يحاول get_full_name() (first_name + last_name).
            2. إذا كان فارغاً → يُرجع username كاحتياط.

        مثال:
            البائع: {first_name: "أحمد", last_name: "علي"} → "أحمد علي"
            البائع: {first_name: "",    username: "ahmed"} → "ahmed"
        """
        if not obj.vendor:
            return "مجهول"
        full_name = obj.vendor.get_full_name()
        return full_name.strip() or obj.vendor.username

    def get_is_in_stock(self, obj: Product) -> bool:
        """
        يُرجع True إذا كان المخزون أكبر من الصفر.

        مثال الـ Response:
            {"stock": 5, "is_in_stock": true}
            {"stock": 0, "is_in_stock": false}
        """
        return obj.stock > 0

    def get_final_price(self, obj: Product):
        """
        يُرجع السعر النهائي الذي يدفعه المشتري.

        المنطق:
            - إذا وُجد discount_price وكان أقل من price → discount_price.
            - وإلا → price الأصلي.

        نستخدم نوع البيانات الأصلي (Decimal) للحفاظ على دقة العمليات المالية.

        مثال:
            price=100, discount_price=75  → 75   (يوجد خصم)
            price=100, discount_price=None → 100  (لا يوجد خصم)
            price=100, discount_price=120 → 100  (خصم غير صالح → نتجاهله)
        """
        if obj.discount_price and obj.discount_price < obj.price:
            return obj.discount_price
        return obj.price

    def get_discount_percentage(self, obj: Product) -> int:
        """
        نسبة الخصم كعدد صحيح (%).

        الصيغة:
            discount_percentage = round((price - discount_price) / price * 100)

        مثال:
            price=200, discount_price=150 → round(50/200*100) = 25 (%)
            price=100, discount_price=None → 0

        يُرجع 0 إذا لم يكن هناك خصم أو كانت البيانات غير منطقية.
        """
        if (
            obj.discount_price
            and obj.discount_price < obj.price
            and obj.price > 0
        ):
            saving = obj.price - obj.discount_price
            return round((saving / obj.price) * 100)
        return 0

    def get_image_main(self, obj: Product) -> str | None:
        """
        يبني رابطاً كاملاً (Absolute URL) للصورة الرئيسية.

        السلوك حسب الحالة:
            ① لا توجد صورة          → None
            ② request موجود في context → Absolute URL: "https://domain.com/media/..."
            ③ request غير موجود      → Relative URL:  "/media/products/image.jpg"

        ⚠️ لضمان Absolute URL، يجب تمرير `request` في context عند إنشاء الـ Serializer.

        الاستخدام في الـ View (يدوياً):
            serializer = ProductSerializer(
                product,
                context={'request': request}
            )

        الاستخدام في الـ ViewSet (تلقائياً):
            # DRF يُمرر request في context تلقائياً عند استخدام get_serializer()
            serializer = self.get_serializer(product)
        """
        if not obj.image_main:
            return None

        request = self.context.get('request')
        url     = obj.image_main.url  # Relative URL من Django Storage

        if request is not None:
            # build_absolute_uri: يُضيف البروتوكول (http/https) والـ domain تلقائياً
            return request.build_absolute_uri(url)

        # احتياط: يُرجع Relative URL إذا لم يُوجد request في context
        return url


# ══════════════════════════════════════════════════════════════════════════════
# 3. ProductCreateUpdateSerializer — إنشاء وتعديل المنتج (Write)
# ══════════════════════════════════════════════════════════════════════════════

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer مخصص لعمليات الكتابة: POST (إنشاء)، PUT/PATCH (تعديل).

    الفروق الجوهرية عن ProductSerializer:
        ✔ category_id  → يقبل رقم ID بدلاً من كائن متداخل (أبسط للـ Client).
        ✔ vendor       → read_only، يُعيَّن تلقائياً في الـ View.
        ✔ validate_*() → تحقق من صحة كل حقل على حدة.
        ✔ validate()   → تحقق من العلاقة بين price وdiscount_price.
        ✔ to_representation() → الـ Response تعود بـ ProductSerializer الكامل.

    مثال على Request Body:
        {
            "name": "هاتف ذكي X",
            "category_id": 3,
            "price": "999.00",
            "discount_price": "799.00",
            "stock": 50
        }

    مثال على Response (بعد الحفظ):
        {
            "id": 42,
            "name": "هاتف ذكي X",
            "category": {"id": 3, "name": "الإلكترونيات", "slug": "electronics"},
            "seller_name": "أحمد علي",
            "final_price": "799.00",
            "discount_percentage": 20,
            ...
        }

    الاستخدام في الـ ViewSet:
        class ProductViewSet(ModelViewSet):
            def get_serializer_class(self):
                if self.action in ['create', 'update', 'partial_update']:
                    return ProductCreateUpdateSerializer
                return ProductSerializer

            def perform_create(self, serializer):
                # يُعيَّن البائع هنا وليس في الـ Serializer
                serializer.save(vendor=self.request.user)
    """

    # ── vendor: read_only ──────────────────────────────────────────────────────
    # يُعيَّن في الـ View عبر: serializer.save(vendor=request.user)
    # جعله read_only يمنع أي مستخدم من انتحال هوية بائع آخر.
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)

    # ── category_id ────────────────────────────────────────────────────────────
    # يقبل رقم ID من Request Body: {"category_id": 5}
    # source='category'  → يُخبر DRF بربطه بحقل `category` في النموذج.
    # write_only=True    → لا يظهر في الـ Response (نُعرضه عبر to_representation).
    # queryset مُقيَّد   → يقبل فقط التصنيفات النشطة (is_active=True).
    category_id = serializers.PrimaryKeyRelatedField(
        queryset       = Category.objects.filter(is_active=True),
        source         = 'category',
        write_only     = True,
        error_messages = {
            'does_not_exist': 'التصنيف المحدد (id={pk_value}) غير موجود أو غير نشط.',
            'incorrect_type': 'معرّف التصنيف يجب أن يكون رقماً صحيحاً، وليس {data_type}.',
            'required':       'حقل category_id مطلوب.',
        },
    )

    class Meta:
        model  = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'category_id',    # ← Write: يقبل ID
            'vendor',         # ← Read-only: يُعرض ID فقط (الاسم في to_representation)
            'price',
            'discount_price',
            'stock',
            'image_main',
            'is_active',
            'is_featured',
        ]
        extra_kwargs = {
            # slug اختياري: يُولَّد تلقائياً من name في النموذج (pre_save / signal)
            'slug': {
                'required':    False,
                'allow_blank': True,
            },
            # discount_price اختياري: قد يكون null (لا يوجد خصم)
            'discount_price': {
                'required':   False,
                'allow_null': True,
            },
            # image_main اختياري: قد لا تُرفع صورة عند الإنشاء
            'image_main': {
                'required':   False,
                'allow_null': True,
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # Field-Level Validation — تحقق من صحة كل حقل مستقل
    # ══════════════════════════════════════════════════════════════════════════

    def validate_price(self, value):
        """
        السعر يجب أن يكون موجباً وأكبر من الصفر.
        DRF يستدعي هذه الدالة تلقائياً عند التحقق من حقل `price`.
        """
        if value <= 0:
            raise serializers.ValidationError(
                "يجب أن يكون السعر أكبر من الصفر."
            )
        return value

    def validate_stock(self, value):
        """
        المخزون يجب أن يكون صفراً أو أكثر.
        المخزون السالب غير منطقي في سياق المتجر الإلكتروني.
        """
        if value < 0:
            raise serializers.ValidationError(
                "لا يمكن أن يكون المخزون سالباً."
            )
        return value

    def validate_name(self, value):
        """الاسم يجب ألا يكون فارغاً بعد إزالة المسافات."""
        if not value.strip():
            raise serializers.ValidationError(
                "اسم المنتج لا يمكن أن يكون فارغاً."
            )
        return value.strip()

    # ══════════════════════════════════════════════════════════════════════════
    # Object-Level Validation — تحقق من صحة العلاقات بين الحقول
    # ══════════════════════════════════════════════════════════════════════════

    def validate(self, attrs):
        """
        تحقق من صحة العلاقة بين price وdiscount_price.

        تعامل ذكي مع PATCH (التعديل الجزئي):
            - عند PATCH، قد لا يُرسَل كلا الحقلين في نفس الوقت.
            - نستخدم dict.get(key, default) بدلاً من or لتجنب مشكلة القيمة 0.
            - نرجع للكائن الحالي (self.instance) لجلب القيمة الحالية.

        مثال على سيناريو PATCH:
            PATCH {"discount_price": 80}  (بدون إرسال price)
            → نجلب price من self.instance.price لإجراء المقارنة.
        """
        # نجلب القيمة من attrs أولاً، ثم من الكائن الحالي كاحتياط
        price = attrs.get(
            'price',
            getattr(self.instance, 'price', None),
        )
        discount_price = attrs.get(
            'discount_price',
            getattr(self.instance, 'discount_price', None),
        )

        if discount_price is not None:
            # التحقق: سعر الخصم يجب أن يكون موجباً
            if discount_price <= 0:
                raise serializers.ValidationError({
                    'discount_price': "يجب أن يكون سعر الخصم أكبر من الصفر."
                })

            # التحقق: سعر الخصم يجب أن يكون أقل من السعر الأصلي
            if price is not None and discount_price >= price:
                raise serializers.ValidationError({
                    'discount_price': (
                        f"يجب أن يكون سعر الخصم ({discount_price}) "
                        f"أقل من السعر الأصلي ({price})."
                    )
                })

        return attrs

    # ══════════════════════════════════════════════════════════════════════════
    # to_representation — تحويل الـ Response لصيغة غنية بعد الحفظ
    # ══════════════════════════════════════════════════════════════════════════

    def to_representation(self, instance):
        """
        يُعيد استخدام ProductSerializer لتوليد الـ Response الكاملة.

        لماذا هذا مهم؟
            - الـ Client يُرسل: {"category_id": 5, "price": "99.99"}
            - بدون هذه الدالة، الـ Response ستعود بنفس صيغة المدخلات (بسيطة).
            - معها، الـ Response تعود بصيغة ProductSerializer الكاملة:
              {"category": {"id": 5, "name": "إلكترونيات"}, "final_price": ...}

        ملاحظة: نُمرر context كاملاً لضمان بناء Absolute URL للصور.
        """
        return ProductSerializer(
            instance,
            context=self.context,  # ضروري لـ get_image_main → request.build_absolute_uri
        ).data