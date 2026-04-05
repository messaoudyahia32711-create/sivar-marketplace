# apps/reviews/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer, CreateReviewSerializer


# ============================================================
# 1) ReviewListView — عرض قائمة التقييمات لمنتج أو خدمة
# ============================================================
class ReviewListView(APIView):
    """
    GET /api/reviews/?product_id=3
    GET /api/reviews/?service_id=7

    عرض جميع التقييمات المرتبطة بمنتج أو خدمة محددة.
    يجب تمرير أحد المعرّفين كـ Query Parameter.
    متاح للجميع بدون تسجيل دخول.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        # ------------------------------------------------
        # 1. استخراج الـ Query Parameters
        # ------------------------------------------------
        product_id = request.query_params.get('product_id')
        service_id = request.query_params.get('service_id')

        # ------------------------------------------------
        # 2. التحقق: يجب تقديم معرّف واحد على الأقل
        # ------------------------------------------------
        if not product_id and not service_id:
            return Response(
                {
                    'error': 'يجب تقديم product_id أو service_id كمعامل بحث.',
                    'usage': [
                        '/api/reviews/?product_id=<id>',
                        '/api/reviews/?service_id=<id>',
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------
        # 3. التحقق: عدم تقديم كلا المعرّفين معاً (XOR)
        # ------------------------------------------------
        if product_id and service_id:
            return Response(
                {
                    'error': 'يجب تقديم product_id أو service_id، وليس كلاهما معاً.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------
        # 4. بناء الـ QuerySet بناءً على المعرّف المُقدَّم
        # ------------------------------------------------
        if product_id:
            reviews = Review.objects.filter(
                product_id=product_id
            ).select_related('user').order_by('-created_at')
        else:
            reviews = Review.objects.filter(
                service_id=service_id
            ).select_related('user').order_by('-created_at')

        # ------------------------------------------------
        # 5. تحويل البيانات وإرجاع الاستجابة
        # ------------------------------------------------
        serializer = ReviewSerializer(reviews, many=True)

        return Response(
            {
                'count': reviews.count(),
                'results': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# 2) CreateReviewView — إنشاء تقييم جديد
# ============================================================
class CreateReviewView(APIView):
    """
    POST /api/reviews/create/

    إنشاء تقييم جديد لمنتج أو خدمة.
    يتطلب تسجيل دخول المستخدم.

    Body (JSON):
    {
        "product_id": 3,       // أو "service_id": 7
        "rating": 5,
        "comment": "ممتاز!"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ------------------------------------------------
        # 1. تمرير البيانات مع الـ context (يحتوي request)
        #    الـ Serializer يحتاج request لاستخراج المستخدم
        #    ولتنفيذ تحقق الـ Uniqueness
        # ------------------------------------------------
        serializer = CreateReviewSerializer(
            data=request.data,
            context={'request': request},
        )

        # ------------------------------------------------
        # 2. التحقق من صحة البيانات
        #    - XOR Logic (product أو service)
        #    - Existence (هل الكيان موجود؟)
        #    - Uniqueness (هل سبق التقييم؟)
        #    كل هذا يحدث داخل serializer.validate()
        # ------------------------------------------------
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'بيانات غير صالحة.',
                    'details': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------
        # 3. إنشاء التقييم
        #    - تعيين user تلقائياً من request.user
        #    - ربط product أو service
        #    - to_representation يُرجع بيانات ReviewSerializer
        # ------------------------------------------------
        review = serializer.save()

        return Response(
            {
                'message': 'تم إنشاء التقييم بنجاح.',
                'review': serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# 3) UserReviewsView — تقييمات المستخدم الحالي
# ============================================================
class UserReviewsView(APIView):
    """
    GET /api/reviews/me/

    جلب جميع التقييمات التي كتبها المستخدم الحالي.
    يتطلب تسجيل دخول.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ------------------------------------------------
        # 1. جلب تقييمات المستخدم الحالي فقط
        #    select_related لتحسين الأداء وتقليل الـ queries
        #    نجلب بيانات product و service مسبقاً
        # ------------------------------------------------
        reviews = Review.objects.filter(
            user=request.user
        ).select_related(
            'user',
            'product',
            'service',
        ).order_by('-created_at')

        # ------------------------------------------------
        # 2. تحويل البيانات باستخدام ReviewSerializer
        # ------------------------------------------------
        serializer = ReviewSerializer(reviews, many=True)

        return Response(
            {
                'count': reviews.count(),
                'results': serializer.data,
            },
            status=status.HTTP_200_OK,
        )