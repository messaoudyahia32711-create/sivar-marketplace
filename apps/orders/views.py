from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.cart.views import CartMixin
from .models import Order
from .serializers import CreateOrderSerializer, OrderSerializer


# ══════════════════════════════════════════════════════════════
# 1) إنشاء طلب جديد - OrderCreateView
#    متاح للمستخدمين المسجلين والزوار على حدٍّ سواء
# ══════════════════════════════════════════════════════════════

class OrderCreateView(CartMixin, APIView):
    """
    POST /api/orders/create/

    يستقبل بيانات الشحن والدفع من الزبون، ويُنشئ طلباً
    جديداً بناءً على محتويات السلة الحالية.

    سير العمل:
        1. جلب السلة عبر CartMixin (سواء بالجلسة أو بالمستخدم)
        2. تمرير السلة والـ request إلى CreateOrderSerializer
        3. التحقق من صحة البيانات
        4. إنشاء الطلب
        5. إرجاع تفاصيل الطلب الكاملة

    يقبل:
        {
            "first_name": "أحمد",
            "last_name": "بن علي",
            "phone_number": "0555123456",
            "email": "ahmed@example.com",        // اختياري
            "wilaya_id": 16,
            "commune_id": 421,
            "address": "حي 500 مسكن، عمارة 12",
            "payment_method": "cod"
        }

    يُرجع:
        201: تفاصيل الطلب الكاملة (OrderSerializer)
        400: أخطاء التحقق
    """

    def post(self, request):
        # ── الخطوة 1: جلب السلة الحالية عبر CartMixin ──
        cart = self.get_cart(request)

        # ── الخطوة 2: تهيئة السيريالايزر مع الـ context ──
        serializer = CreateOrderSerializer(
            data=request.data,
            context={
                'request': request,
                'cart': cart,
            },
        )

        # ── الخطوة 3: التحقق وإنشاء الطلب ──
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ── الخطوة 4: إرجاع الاستجابة ──
        # to_representation في CreateOrderSerializer يُحوّل
        # الناتج تلقائياً إلى صيغة OrderSerializer
        return Response(
            {
                'message': 'تم إنشاء الطلب بنجاح.',
                'order': serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ══════════════════════════════════════════════════════════════
# 2) قائمة طلبات المستخدم - OrderListView
#    متاح فقط للمستخدمين المسجلين
# ══════════════════════════════════════════════════════════════

class OrderListView(APIView):
    """
    GET /api/orders/

    يعرض جميع طلبات المستخدم المسجّل مرتّبة من الأحدث
    إلى الأقدم.

    الزوار (غير المسجلين) لا يمكنهم الوصول لهذا الـ endpoint،
    ويتلقّون استجابة 401 Unauthorized.

    يُرجع:
        200: قائمة الطلبات
        401: غير مصرّح (زائر)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ── جلب طلبات المستخدم الحالي فقط ──
        orders = Order.objects.filter(
            user=request.user,
        ).select_related(
            'wilaya',
            'commune',
        ).prefetch_related(
            'items__product',
            'items__service',
        ).order_by('-created_at')

        # ── بناء الاستجابة ──
        serializer = OrderSerializer(orders, many=True)

        return Response(
            {
                'count': orders.count(),
                'orders': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ══════════════════════════════════════════════════════════════
# 3) تفاصيل طلب محدد - OrderDetailView
#    متاح فقط للمستخدمين المسجلين (مع التحقق من الملكية)
# ══════════════════════════════════════════════════════════════

class OrderDetailView(APIView):
    """
    GET /api/orders/<order_id>/

    يعرض التفاصيل الكاملة لطلب محدد، بما في ذلك
    جميع عناصره.

    الحماية:
        1. المستخدم يجب أن يكون مسجلاً (IsAuthenticated)
        2. الطلب يجب أن يكون ملكاً للمستخدم الحالي

    يُرجع:
        200: تفاصيل الطلب
        401: غير مصرّح (زائر)
        404: الطلب غير موجود أو لا يخصّ هذا المستخدم
    """

    permission_classes = [IsAuthenticated]

    def get_order(self, order_id, user):
        """
        جلب الطلب مع التحقق من الملكية.
        يُرجع (order, None) عند النجاح،
        أو (None, Response) عند الفشل.
        """
        try:
            order = Order.objects.select_related(
                'wilaya',
                'commune',
            ).prefetch_related(
                'items__product',
                'items__service',
            ).get(id=order_id)
        except Order.DoesNotExist:
            return None, Response(
                {'error': 'الطلب غير موجود.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ── التحقق من الملكية ──
        if order.user != user:
            # نُرجع 404 بدلاً من 403 لعدم كشف وجود الطلب
            return None, Response(
                {'error': 'الطلب غير موجود.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return order, None

    def get(self, request, order_id):
        # ── جلب الطلب مع التحقق ──
        order, error_response = self.get_order(order_id, request.user)

        if error_response:
            return error_response

        # ── بناء الاستجابة ──
        serializer = OrderSerializer(order)

        return Response(
            {'order': serializer.data},
            status=status.HTTP_200_OK,
        )
