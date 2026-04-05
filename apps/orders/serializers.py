from rest_framework import serializers

from apps.localization.models import Wilaya, Commune
from .models import Order, OrderItem


# ══════════════════════════════════════════════
# 1) سيريالايزر عناصر الطلب - OrderItemSerializer
#    للقراءة فقط: يعرض تفاصيل كل منتج/خدمة داخل الطلب
# ══════════════════════════════════════════════

class OrderItemSerializer(serializers.ModelSerializer):
    """
    يعرض تفاصيل عنصر واحد من عناصر الطلب.
    يُستخدم كـ Nested Serializer داخل OrderSerializer.

    الحقول المعروضة:
        - اسم المنتج أو الخدمة (نصّي بدلاً من ID)
        - السعر الإفرادي
        - الكمية
        - المجموع الفرعي (السعر × الكمية)
    """

    # ── حقول مخصّصة: عرض الاسم بدلاً من الـ ID ──
    product_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()

    # ── حقل محسوب: المجموع الفرعي ──
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product_name',
            'service_name',
            'price',
            'quantity',
            'subtotal',
        )
        # جميع الحقول للقراءة فقط
        read_only_fields = fields

    def get_product_name(self, obj):
        """إرجاع اسم المنتج إن وُجد، وإلا None."""
        return obj.product.name if obj.product else None

    def get_service_name(self, obj):
        """إرجاع اسم الخدمة إن وُجدت، وإلا None."""
        return obj.service.name if obj.service else None

    def get_subtotal(self, obj):
        """
        حساب المجموع الفرعي: السعر × الكمية.
        نستدعي خاصية subtotal من الموديل إن وُجدت،
        وإلا نحسبها يدوياً.
        """
        if hasattr(obj, 'subtotal') and callable(getattr(obj, 'subtotal', None)):
            return str(obj.subtotal())
        return str(obj.price * obj.quantity)


# ══════════════════════════════════════════════
# 2) سيريالايزر الطلب - OrderSerializer
#    للقراءة فقط: يعرض تفاصيل الطلب الكاملة
# ══════════════════════════════════════════════

class OrderSerializer(serializers.ModelSerializer):
    """
    يعرض تفاصيل طلب كامل مع عناصره.
    يُستخدم في: قائمة الطلبات، تفاصيل طلب واحد.

    يتضمّن:
        - معلومات الزبون
        - عنوان الشحن (اسم الولاية والبلدية بدلاً من ID)
        - حالة الطلب والدفع
        - قائمة العناصر (Nested)
    """

    # ── عرض اسم الولاية والبلدية بدلاً من الـ ID ──
    wilaya_name = serializers.CharField(
        source='wilaya.name',
        read_only=True,
    )
    commune_name = serializers.CharField(
        source='commune.name',
        read_only=True,
    )

    # ── عرض النص المقروء للحقول ذات الخيارات ──
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True,
    )

    # ── عناصر الطلب (Nested Serializer) ──
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            # معلومات الزبون
            'first_name',
            'last_name',
            'phone_number',
            'email',
            # معلومات الشحن
            'wilaya',
            'wilaya_name',
            'commune',
            'commune_name',
            'address',
            # معلومات الفاتورة
            'status',
            'status_display',
            'payment_method',
            'payment_method_display',
            'is_paid',
            'total_price',
            # عناصر الطلب
            'items',
            # التواريخ
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


# ══════════════════════════════════════════════
# 3) سيريالايزر إنشاء الطلب - CreateOrderSerializer
#    للكتابة فقط: يستقبل بيانات الزبون ويُنشئ الطلب
# ══════════════════════════════════════════════

class CreateOrderSerializer(serializers.Serializer):
    """
    يستقبل بيانات إنهاء الطلب (Checkout) من الزبون.

    سير العمل:
        1. التحقق من صحة البيانات المُدخلة
        2. التحقق من أن الولاية والبلدية موجودة ومترابطة
        3. جلب السلة من الـ context والتأكد أنها ليست فارغة
        4. استدعاء Order.create_from_cart لإنشاء الطلب
        5. إرجاع كائن الطلب

    الاستخدام في الـ View:
        serializer = CreateOrderSerializer(
            data=request.data,
            context={
                'request': request,
                'cart': cart_instance,
            }
        )
    """

    # ── معلومات الزبون ──
    first_name = serializers.CharField(
        max_length=50,
        error_messages={
            'required': 'الاسم الأول مطلوب.',
            'blank': 'الاسم الأول لا يمكن أن يكون فارغاً.',
        },
    )
    last_name = serializers.CharField(
        max_length=50,
        error_messages={
            'required': 'اسم العائلة مطلوب.',
            'blank': 'اسم العائلة لا يمكن أن يكون فارغاً.',
        },
    )
    phone_number = serializers.CharField(
        max_length=15,
        error_messages={
            'required': 'رقم الهاتف مطلوب.',
        },
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': 'يرجى إدخال بريد إلكتروني صحيح.',
        },
    )

    # ── معلومات الشحن ──
    wilaya_id = serializers.IntegerField(
        error_messages={
            'required': 'يرجى اختيار الولاية.',
            'invalid': 'معرّف الولاية غير صالح.',
        },
    )
    commune_id = serializers.IntegerField(
        error_messages={
            'required': 'يرجى اختيار البلدية.',
            'invalid': 'معرّف البلدية غير صالح.',
        },
    )
    address = serializers.CharField(
        max_length=255,
        error_messages={
            'required': 'العنوان مطلوب.',
            'blank': 'العنوان لا يمكن أن يكون فارغاً.',
        },
    )

    # ── طريقة الدفع ──
    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices,
        error_messages={
            'required': 'يرجى اختيار طريقة الدفع.',
            'invalid_choice': 'طريقة الدفع المحددة غير متاحة.',
        },
    )

    # ──────────────────────────────────────────
    # التحققات (Validation)
    # ──────────────────────────────────────────

    def validate_phone_number(self, value):
        """
        التحقق من أن رقم الهاتف يتكوّن من أرقام فقط
        وأن طوله منطقي (بين 9 و 15 رقماً).
        """
        # إزالة المسافات والشرطات
        cleaned = value.replace(' ', '').replace('-', '').replace('+', '')

        if not cleaned.isdigit():
            raise serializers.ValidationError(
                'رقم الهاتف يجب أن يحتوي على أرقام فقط.'
            )

        if len(cleaned) < 9 or len(cleaned) > 15:
            raise serializers.ValidationError(
                'رقم الهاتف يجب أن يكون بين 9 و 15 رقماً.'
            )

        return value

    def validate_wilaya_id(self, value):
        """التحقق من أن الولاية موجودة في قاعدة البيانات."""
        if not Wilaya.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'الولاية المحددة غير موجودة.'
            )
        return value

    def validate_commune_id(self, value):
        """التحقق من أن البلدية موجودة في قاعدة البيانات."""
        if not Commune.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'البلدية المحددة غير موجودة.'
            )
        return value

    def validate(self, attrs):
        """
        تحقق مشترك (Cross-field Validation):
        1. التأكد من أن البلدية تتبع الولاية المحددة.
        2. التأكد من أن السلة ليست فارغة.
        """
        wilaya_id = attrs.get('wilaya_id')
        commune_id = attrs.get('commune_id')

        # ── التحقق من ترابط الولاية والبلدية ──
        if wilaya_id and commune_id:
            commune_belongs_to_wilaya = Commune.objects.filter(
                id=commune_id,
                wilaya_id=wilaya_id,
            ).exists()

            if not commune_belongs_to_wilaya:
                raise serializers.ValidationError({
                    'commune_id': 'البلدية المحددة لا تتبع الولاية المختارة.',
                })

        # ── التحقق من أن السلة ليست فارغة ──
        cart = self.context.get('cart')

        if cart is None:
            raise serializers.ValidationError(
                'لا توجد سلة مرتبطة بهذا الطلب.'
            )

        # التحقق من وجود عناصر في السلة
        if not cart.items.exists():
            raise serializers.ValidationError(
                'السلة فارغة. أضف منتجات قبل إنهاء الطلب.'
            )

        return attrs

    # ──────────────────────────────────────────
    # إنشاء الطلب (Create)
    # ──────────────────────────────────────────

    def create(self, validated_data):
        """
        إنشاء طلب جديد من بيانات السلة.

        الخطوات:
            1. جلب السلة والمستخدم من الـ context
            2. جلب كائنات الولاية والبلدية
            3. استدعاء Order.create_from_cart لإنشاء الطلب وعناصره
            4. إرجاع كائن الطلب الجديد
        """
        request = self.context.get('request')
        cart = self.context.get('cart')

        # جلب كائنات الولاية والبلدية
        wilaya = Wilaya.objects.get(id=validated_data['wilaya_id'])
        commune = Commune.objects.get(id=validated_data['commune_id'])

        # تحديد المستخدم (مسجّل أو زائر)
        user = request.user if request.user.is_authenticated else None

        # استدعاء الكلاس ميثود لإنشاء الطلب
        order = Order.create_from_cart(
            cart=cart,
            user=user,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', ''),
            wilaya=wilaya,
            commune=commune,
            address=validated_data['address'],
            payment_method=validated_data['payment_method'],
        )

        return order

    def to_representation(self, instance):
        """
        بعد الإنشاء، نُعيد تفاصيل الطلب الكاملة
        باستخدام OrderSerializer بدلاً من الحقول المُدخلة.
        """
        return OrderSerializer(instance, context=self.context).data