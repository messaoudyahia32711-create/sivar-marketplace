# apps/reviews/serializers.py

from rest_framework import serializers
from apps.reviews.models import Review
from apps.products.models import Product
from apps.services.models import Service


# ============================================================
# 1) ReviewSerializer — للقراءة والعرض (Read / Display)
# ============================================================
class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer مخصص لعرض التقييمات للمستخدمين.
    يُظهر اسم المستخدم بدلاً من الـ ID،
    ويُضيف حقلاً بصرياً للنجوم (★☆).
    """

    # ---- حقول مُحسَّنة ----
    # عرض اسم المستخدم الكامل بدلاً من الـ Foreign Key ID
    user_name = serializers.SerializerMethodField()

    # تمثيل مرئي للنجوم مثل: ★★★★☆
    stars_display = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'user_name',
            'rating',
            'comment',
            'stars_display',
            'created_at',
        ]
        # جميع الحقول للقراءة فقط في هذا الـ Serializer
        read_only_fields = fields

    def get_user_name(self, obj):
        """
        إرجاع الاسم الكامل للمستخدم إن وُجد،
        وإلا إرجاع الـ username كبديل.
        """
        full_name = obj.user.get_full_name()
        return full_name if full_name.strip() else obj.user.username

    def get_stars_display(self, obj):
        """
        تحويل التقييم الرقمي إلى تمثيل بصري بالنجوم.
        مثال: rating=4 من 5  ←  '★★★★☆'
        """
        max_stars = 5
        filled = int(obj.rating)                  # نجوم ممتلئة
        empty = max_stars - filled                 # نجوم فارغة
        return '★' * filled + '☆' * empty


# ============================================================
# 2) CreateReviewSerializer — للكتابة والإنشاء (Create)
# ============================================================
class CreateReviewSerializer(serializers.Serializer):
    """
    Serializer مخصص لإنشاء تقييم جديد.
    يدعم تقييم منتج (Product) أو خدمة (Service)
    مع ضمان منطق XOR: يجب اختيار واحد فقط منهما.
    """

    # ---- حقول الإدخال ----
    product_id = serializers.IntegerField(
        required=False,          # اختياري
        allow_null=True,
        help_text="معرّف المنتج المراد تقييمه (اختياري إذا تم تقديم service_id)"
    )
    service_id = serializers.IntegerField(
        required=False,          # اختياري
        allow_null=True,
        help_text="معرّف الخدمة المراد تقييمها (اختياري إذا تم تقديم product_id)"
    )
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        help_text="التقييم من 1 إلى 5"
    )
    comment = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        default='',
        help_text="تعليق المستخدم (اختياري)"
    )

    # ========================================================
    #  التحققات (Validation)
    # ========================================================

    def validate(self, attrs):
        """
        تحقق شامل على مستوى الـ Serializer بالكامل.
        يتضمن ثلاثة مستويات:
          1. XOR Logic  — منتج أو خدمة، وليس كلاهما ولا بدونهما.
          2. Existence   — التأكد من وجود الكيان في قاعدة البيانات.
          3. Uniqueness  — منع التقييم المكرر لنفس المستخدم.
        """
        product_id = attrs.get('product_id')
        service_id = attrs.get('service_id')

        # استخراج المستخدم الحالي من الـ Request Context
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError(
                "لا يمكن تحديد المستخدم. تأكد من تمرير request في context."
            )
        user = request.user

        # ------------------------------------------------
        # 1) XOR Logic: يجب تقديم واحد فقط
        # ------------------------------------------------
        has_product = product_id is not None
        has_service = service_id is not None

        if has_product == has_service:
            # كلاهما موجود أو كلاهما غائب
            raise serializers.ValidationError({
                'non_field_errors': [
                    "يجب تقديم إما product_id أو service_id، وليس كلاهما أو لا شيء."
                ]
            })

        # ------------------------------------------------
        # 2) Existence: التأكد من وجود الكيان
        # ------------------------------------------------
        if has_product:
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError({
                    'product_id': f"لا يوجد منتج بالمعرّف {product_id}."
                })
            # تخزين الكائن للاستخدام لاحقاً في create()
            attrs['product'] = product
            attrs['service'] = None

        if has_service:
            try:
                service = Service.objects.get(pk=service_id)
            except Service.DoesNotExist:
                raise serializers.ValidationError({
                    'service_id': f"لا توجد خدمة بالمعرّف {service_id}."
                })
            attrs['service'] = service
            attrs['product'] = None

        # ------------------------------------------------
        # 3) Uniqueness: منع التقييم المكرر
        # ------------------------------------------------
        if has_product:
            if Review.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError({
                    'product_id': "لقد قمت بتقييم هذا المنتج مسبقاً."
                })

        if has_service:
            if Review.objects.filter(user=user, service=service).exists():
                raise serializers.ValidationError({
                    'service_id': "لقد قمت بتقييم هذه الخدمة مسبقاً."
                })

        return attrs

    # ========================================================
    #  الإنشاء (Create)
    # ========================================================

    def create(self, validated_data):
        """
        إنشاء كائن Review جديد.
        - يتم تعيين المستخدم تلقائياً من request.user.
        - يتم ربط المنتج أو الخدمة بناءً على الإدخال.
        """
        request = self.context['request']

        review = Review.objects.create(
            user=request.user,
            product=validated_data.get('product'),
            service=validated_data.get('service'),
            rating=validated_data['rating'],
            comment=validated_data.get('comment', ''),
        )

        return review

    def to_representation(self, instance):
        """
        بعد الإنشاء، نُعيد البيانات بتنسيق ReviewSerializer
        لعرض التقييم بشكل كامل ومنسّق للمستخدم.
        """
        return ReviewSerializer(instance, context=self.context).data
