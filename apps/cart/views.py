from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny

from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer


class CartMixin:
    """
    Mixin مشترك لجميع Views السلة.
    يوفر منطق تحديد السلة للمستخدم المسجل أو الزائر.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get_or_create_cart(self, request):
        """جلب أو إنشاء سلة بناءً على نوع المستخدم."""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)

        return cart

    def get_cart(self, request):
        """جلب السلة الحالية بدون إنشاء واحدة جديدة."""
        if request.user.is_authenticated:
            return Cart.objects.filter(user=request.user).first()

        session_key = request.session.session_key
        if not session_key:
            return None

        return Cart.objects.filter(session_key=session_key).first()


# ──────────────────────────────────────────────
# 1) عرض تفاصيل السلة
# ──────────────────────────────────────────────
class CartDetailView(CartMixin, APIView):
    """
    GET: جلب أو إنشاء سلة التسوق وإرجاع تفاصيلها.
    """

    def get(self, request):
        cart = self.get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# 2) إضافة عنصر إلى السلة
# ──────────────────────────────────────────────
class AddToCartView(CartMixin, APIView):
    """
    POST: إضافة عنصر جديد إلى السلة أو تحديث الكمية إذا كان موجوداً.
    الحقول المطلوبة: item_type, item_id, quantity
    """

    def post(self, request):
        cart = self.get_or_create_cart(request)

        serializer = AddToCartSerializer(
            data=request.data,
            context={'cart': cart, 'request': request},
        )

        if serializer.is_valid():
            serializer.save()
            # إرجاع السلة كاملة بعد الإضافة
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────
# 3) تعديل أو حذف عنصر من السلة
# ──────────────────────────────────────────────
class CartItemDetailView(CartMixin, APIView):
    """
    PATCH  : تعديل كمية عنصر في السلة.
    DELETE : حذف عنصر من السلة.
    """

    def get_cart_item(self, request, item_id):
        """
        جلب عنصر السلة مع التحقق من الملكية.
        يُرجع (cart_item, None) عند النجاح أو (None, Response) عند الفشل.
        """
        cart = self.get_cart(request)
        if not cart:
            return None, Response(
                {'detail': 'السلة غير موجودة.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return None, Response(
                {'detail': 'العنصر غير موجود في سلتك.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return cart_item, None

    # ── تعديل الكمية ──
    def patch(self, request, item_id):
        cart_item, error_response = self.get_cart_item(request, item_id)
        if error_response:
            return error_response

        serializer = UpdateCartItemSerializer(
            cart_item,
            data=request.data,
            partial=True,
            context={'request': request},
        )

        if serializer.is_valid():
            serializer.save()
            cart_serializer = CartSerializer(cart_item.cart)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ── حذف عنصر ──
    def delete(self, request, item_id):
        cart_item, error_response = self.get_cart_item(request, item_id)
        if error_response:
            return error_response

        cart = cart_item.cart
        cart_item.delete()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# 4) تفريغ السلة بالكامل
# ──────────────────────────────────────────────
class ClearCartView(CartMixin, APIView):
    """
    DELETE: حذف جميع العناصر من السلة الحالية.
    """

    def delete(self, request):
        cart = self.get_cart(request)

        if not cart:
            return Response(
                {'detail': 'السلة غير موجودة.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart.items.all().delete()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)