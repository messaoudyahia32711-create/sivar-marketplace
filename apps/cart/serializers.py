from decimal import Decimal

from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from apps.products.models import Product
from apps.services.models import Service
from .models import Cart, CartItem


# ╔══════════════════════════════════════════════════════════╗
# ║  1. Nested Serializers — عرض مختصر للمنتج والخدمة       ║
# ╚══════════════════════════════════════════════════════════╝

class ProductMiniSerializer(serializers.ModelSerializer):
    """
    عرض مختصر للمنتج داخل عنصر السلة.
    الهدف: تزويد الـ Frontend بالبيانات الأساسية للعرض
    دون الحاجة لطلب API إضافي.
    """

    class Meta:
        model = Product
        fields = ("id", "name", "slug", "image", "price", "stock")
        # ─── جميعها للقراءة فقط ───
        read_only_fields = fields


class ServiceMiniSerializer(serializers.ModelSerializer):
    """
    عرض مختصر للخدمة داخل عنصر السلة.
    """

    class Meta:
        model = Service
        fields = ("id", "name", "slug", "image", "price")
        read_only_fields = fields


# ╔══════════════════════════════════════════════════════════╗
# ║  2. CartItemSerializer — عرض عنصر واحد في السلة         ║
# ╚══════════════════════════════════════════════════════════╝

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer للقراءة فقط — يعرض تفاصيل عنصر داخل السلة.

    يوفّر:
    - بيانات المنتج أو الخدمة المضمّنة (Nested)
    - نوع العنصر (product / service)
    - إجمالي سعر السطر (السعر × الكمية)
    """

    # ─── بيانات مضمّنة: المنتج والخدمة ───
    product = ProductMiniSerializer(read_only=True)
    service = ServiceMiniSerializer(read_only=True)

    # ─── حقول محسوبة ───
    item_type = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    total_item_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "item_type",
            "item_name",
            "product",
            "service",
            "quantity",
            "price",           # سعر اللقطة (Snapshot) وقت الإضافة
            "total_item_price",
            "added_at",
        )
        read_only_fields = fields

    # ════════════════════════════════════════════
    #  الحقول المحسوبة
    # ════════════════════════════════════════════

    def get_item_type(self, obj) -> str:
        """
        تحديد نوع العنصر لتسهيل التعامل في الـ Frontend.
        Returns: "product" | "service" | "unknown"
        """
        if obj.product_id:
            return "product"
        if obj.service_id:
            return "service"
        return "unknown"

    def get_item_name(self, obj) -> str:
        """اسم العنصر بغض النظر عن نوعه."""
        if obj.product:
            return obj.product.name
        if obj.service:
            return obj.service.name
        return ""

    def get_total_item_price(self, obj) -> str:
        """
        إجمالي سعر السطر = سعر اللقطة × الكمية.
        نُعيده كـ string للحفاظ على دقة الأرقام العشرية.
        """
        return str(obj.line_total)


# ╔══════════════════════════════════════════════════════════╗
# ║  3. CartSerializer — عرض السلة الكاملة                  ║
# ╚══════════════════════════════════════════════════════════╝

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer للقراءة فقط — يعرض السلة بكل عناصرها.

    الاستجابة النموذجية:
    {
        "id": 12,
        "items": [...],
        "items_count": 3,
        "total_price": "1250.00",
        "created_at": "...",
        "updated_at": "..."
    }
    """

    # ─── عناصر السلة مضمّنة ───
    items = CartItemSerializer(many=True, read_only=True)

    # ─── حقول محسوبة ───
    items_count = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "items",
            "items_count",
            "total_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_items_count(self, obj) -> int:
        """
        العدد الإجمالي للوحدات في السلة (مجموع الكميات).
        نستخدم الـ property الموجود في الموديل.
        """
        return obj.items_count

    def get_total_price(self, obj) -> str:
        """المجموع الكلي لجميع عناصر السلة."""
        return str(obj.total_price)


# ╔══════════════════════════════════════════════════════════╗
# ║  4. AddToCartSerializer — إضافة عنصر إلى السلة          ║
# ╚══════════════════════════════════════════════════════════╝

class AddToCartSerializer(serializers.Serializer):
    """
    Serializer للكتابة — يتعامل مع إضافة منتج أو خدمة إلى السلة.

    ─── مسار البيانات ───
    1. Frontend يرسل: { item_type, item_id, quantity }
    2. validate: نتحقق من الوجود + المخزون + نجلب السعر
    3. create: نُنشئ أو نُحدّث CartItem + نربطه بالسلة

    ─── ملاحظة معمارية ───
    نستخدم Serializer وليس ModelSerializer لأن الحقول المُستقبَلة
    (item_id, item_type) تختلف تماماً عن حقول الموديل
    (product, service, price).
    """

    # ─── الحقول المُستقبَلة من الـ Frontend ───
    ITEM_TYPE_CHOICES = (
        ("product", "منتج"),
        ("service", "خدمة"),
    )

    item_type = serializers.ChoiceField(
        choices=ITEM_TYPE_CHOICES,
        help_text='نوع العنصر: "product" أو "service"',
    )

    item_id = serializers.IntegerField(
        min_value=1,
        help_text="معرّف المنتج أو الخدمة",
    )

    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
        help_text="الكمية المطلوبة (1 على الأقل)",
    )

    # ════════════════════════════════════════════
    #  التحقق (Validation)
    # ════════════════════════════════════════════

    def validate_item_id(self, value):
        """
        تحقق أوّلي: هل الـ ID رقم موجب معقول؟
        التحقق من الوجود الفعلي يتم في validate() لأنه يعتمد على item_type.
        """
        if value <= 0:
            raise serializers.ValidationError("معرّف العنصر يجب أن يكون رقماً موجباً.")
        return value

    def validate(self, attrs):
        """
        التحقق المركّب:
        1. هل المنتج/الخدمة موجود فعلاً؟
        2. هل المنتج/الخدمة نشط (متاح)؟
        3. هل المخزون كافٍ (للمنتجات فقط)؟
        4. جلب السعر الحالي كـ Snapshot.
        """
        item_type = attrs["item_type"]
        item_id = attrs["item_id"]
        quantity = attrs["quantity"]

        # ─── 1) جلب العنصر من قاعدة البيانات ───
        if item_type == "product":
            attrs = self._validate_product(attrs, item_id, quantity)
        else:
            attrs = self._validate_service(attrs, item_id)

        return attrs

    def _validate_product(self, attrs, item_id, quantity):
        """
        التحقق الخاص بالمنتجات:
        - الوجود والتفعيل
        - كفاية المخزون مع مراعاة الكمية الموجودة مسبقاً في السلة
        """
        try:
            product = Product.objects.get(pk=item_id, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                {"item_id": "المنتج غير موجود أو غير متاح حالياً."}
            )

        # ─── حساب الكمية الإجمالية (الحالية + الجديدة) ───
        existing_quantity = self._get_existing_quantity(
            product_id=product.pk
        )
        total_requested = existing_quantity + quantity

        # ─── فحص المخزون ───
        if product.stock <= 0:
            raise serializers.ValidationError(
                {"quantity": "عذراً، هذا المنتج غير متوفر في المخزن حالياً."}
            )

        if product.stock < total_requested:
            available = product.stock - existing_quantity
            if available <= 0:
                raise serializers.ValidationError(
                    {"quantity": f"نفدت الكمية! لديك بالفعل {existing_quantity} في سلتك وهي أقصى كمية متاحة."}
                )
            raise serializers.ValidationError(
                {
                    "quantity": (
                        f"الكمية المطلوبة ({quantity}) تتجاوز المتاح. "
                        f"يمكنك إضافة {available} وحدة إضافية فقط."
                    )
                }
            )

        # ─── تخزين الكائن والسعر للاستخدام في create() ───
        attrs["product_obj"] = product
        attrs["service_obj"] = None
        attrs["snapshot_price"] = product.get_final_price()

        return attrs

    def _validate_service(self, attrs, item_id):
        """
        التحقق الخاص بالخدمات:
        - الوجود والتفعيل فقط (الخدمات ليس لها مخزون)
        """
        try:
            service = Service.objects.get(pk=item_id, is_active=True)
        except Service.DoesNotExist:
            raise serializers.ValidationError(
                {"item_id": "الخدمة غير موجودة أو غير متاحة حالياً."}
            )

        attrs["product_obj"] = None
        attrs["service_obj"] = service
        attrs["snapshot_price"] = service.price

        return attrs

    def _get_existing_quantity(self, product_id=None, service_id=None):
        """
        جلب الكمية الموجودة مسبقاً في السلة لنفس العنصر.
        تُستخدم لحساب الكمية الإجمالية عند فحص المخزون.
        """
        cart = self.context.get("cart")
        if not cart or not cart.pk:
            return 0

        filters = {"cart": cart}
        if product_id:
            filters["product_id"] = product_id
        elif service_id:
            filters["service_id"] = service_id
        else:
            return 0

        existing_item = CartItem.objects.filter(**filters).first()
        return existing_item.quantity if existing_item else 0

    # ════════════════════════════════════════════
    #  الإنشاء (Create)
    # ════════════════════════════════════════════

    def create(self, validated_data):
        """
        إضافة العنصر إلى السلة مع التعامل مع التكرار.

        ─── السيناريوهات ───
        أ) العنصر غير موجود في السلة → إنشاء CartItem جديد
        ب) العنصر موجود بالفعل → زيادة الكمية وتحديث السعر

        ─── الأمان ───
        نستخدم transaction.atomic + select_for_update لمنع
        حالات السباق (Race Conditions) عند الإضافة المتزامنة.
        """
        cart = self.context["cart"]
        product = validated_data["product_obj"]
        service = validated_data["service_obj"]
        quantity = validated_data["quantity"]
        price = validated_data["snapshot_price"]

        # ─── بناء مُعرّف البحث الفريد ───
        lookup = {"cart": cart}
        if product:
            lookup["product"] = product
        else:
            lookup["service"] = service

        with transaction.atomic():
            # ─── محاولة إيجاد عنصر موجود (مع قفل) ───
            try:
                existing_item = (
                    CartItem.objects
                    .select_for_update()
                    .get(**lookup)
                )
                # ── السيناريو (ب): زيادة الكمية ──
                existing_item.quantity = F("quantity") + quantity
                existing_item.price = price  # تحديث السعر لآخر لقطة
                existing_item.save(update_fields=["quantity", "price"])
                existing_item.refresh_from_db()
                return existing_item

            except CartItem.DoesNotExist:
                # ── السيناريو (أ): إنشاء عنصر جديد ──
                return CartItem.objects.create(
                    cart=cart,
                    product=product,
                    service=service,
                    quantity=quantity,
                    price=price,
                )


# ╔══════════════════════════════════════════════════════════╗
# ║  5. UpdateCartItemSerializer — تعديل كمية عنصر          ║
# ╚══════════════════════════════════════════════════════════╝

class UpdateCartItemSerializer(serializers.Serializer):
    """
    تعديل كمية عنصر موجود في السلة.
    يُستخدم مع PATCH /cart/items/<id>/

    ─── لماذا Serializer وليس ModelSerializer؟ ───
    لأننا نريد التحكم الكامل في التحقق من المخزون
    قبل السماح بتعديل الكمية.
    """

    quantity = serializers.IntegerField(
        min_value=1,
        help_text="الكمية الجديدة (1 على الأقل)",
    )

    def validate_quantity(self, value):
        """
        التحقق من أن الكمية الجديدة لا تتجاوز المخزون.
        الـ instance هو كائن CartItem الحالي.
        """
        cart_item = self.instance

        # ─── فحص المخزون للمنتجات فقط ───
        if cart_item.product:
            if cart_item.product.stock < value:
                raise serializers.ValidationError(
                    f"الكمية المطلوبة ({value}) تتجاوز المخزون "
                    f"المتاح ({cart_item.product.stock})."
                )

        return value

    def update(self, instance, validated_data):
        """تحديث الكمية وتحديث سعر اللقطة."""
        instance.quantity = validated_data["quantity"]

        # ─── تحديث سعر اللقطة لآخر سعر ───
        if instance.product:
            instance.price = instance.product.price
        elif instance.service:
            instance.price = instance.service.price

        instance.save(update_fields=["quantity", "price"])
        return instance