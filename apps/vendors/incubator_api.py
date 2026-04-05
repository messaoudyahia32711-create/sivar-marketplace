from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q
from rest_framework import status, viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import OrganizationRequest
from apps.users.models import TeamMember

User = get_user_model()

# ──────────────────────────────────────────────
# 1) Serializers
# ──────────────────────────────────────────────

class IncubatorOrgSerializer(serializers.ModelSerializer):
    """عرض المؤسسات المحتضنة مع درجة الأداء."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'university_name', 'performance_score', 'is_verified', 'date_joined']

class TeamMemberSerializer(serializers.ModelSerializer):
    """إدارة أعضاء فريق العمل (حاضنة أو مؤسسة)."""
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'position', 'email', 'phone', 'bio', 'image', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class OrganizationRequestSerializer(serializers.ModelSerializer):
    """طلبات الانضمام."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OrganizationRequest
        fields = ['id', 'name', 'sector', 'status', 'status_display', 'created_at']

# ──────────────────────────────────────────────
# 2) Permissions & Views
# ──────────────────────────────────────────────

class IsIncubatorPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'INCUBATOR'

class OrganizationRequestViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsIncubatorPermission]
    serializer_class = OrganizationRequestSerializer

    def get_queryset(self):
        return OrganizationRequest.objects.filter(incubator=self.request.user).order_by('-created_at')

class IncubatorOrganizationsViewSet(viewsets.ReadOnlyModelViewSet):
    """قائمة المؤسسات التابعة للحاضنة."""
    permission_classes = [IsIncubatorPermission]
    serializer_class = IncubatorOrgSerializer

    def get_queryset(self):
        return User.objects.filter(incubator=self.request.user, role='INSTITUTION')

class IncubatorDashboardStatsAPIView(APIView):
    permission_classes = [IsIncubatorPermission]

    def get(self, request):
        user = request.user
        orgs = User.objects.filter(incubator=user, role='INSTITUTION')
        org_ids = orgs.values_list('id', flat=True)
        
        # 🟢 1) إحصائيات المؤسسات الأساسية
        total_orgs = orgs.count()
        avg_perf = orgs.aggregate(avg=Avg('performance_score'))['avg'] or 0
        active_orgs = orgs.filter(is_verified=True).count()
        weak_orgs = orgs.filter(performance_score__lt=50).count()

        # 🟢 2) مبيعات ونشاط المعارض (Galleries)
        from apps.orders.models import OrderItem
        from apps.products.models import Product
        from apps.services.models import Service
        from django.db.models import Sum, F

        # إجمالي المبيعات (DZD)
        total_revenue = OrderItem.objects.filter(
            Q(product__vendor_id__in=org_ids) | Q(service__vendor_id__in=org_ids)
        ).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0

        # إجمالي الطلبات
        total_orders = OrderItem.objects.filter(
            Q(product__vendor_id__in=org_ids) | Q(service__vendor_id__in=org_ids)
        ).values('order_id').distinct().count()

        # إجمالي المعروضات في المعارض
        gallery_items = Product.objects.filter(vendor_id__in=org_ids).count() + \
                        Service.objects.filter(vendor_id__in=org_ids).count()

        # ترتيب المؤسسات حسب الأداء (Top 5) مع حساب ديناميكي حقيقي
        sorted_orgs = []
        for org in orgs:
            revenue = OrderItem.objects.filter(
                Q(product__vendor_id=org.id) | Q(service__vendor_id=org.id)
            ).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
            
            orders_count = OrderItem.objects.filter(
                Q(product__vendor_id=org.id) | Q(service__vendor_id=org.id)
            ).values('order').distinct().count()
            
            perf_variation = min(50, int((revenue / 50000) * 30) + (orders_count * 2))
            org.calculated_score = min(100, max(0, int(org.performance_score * 0.5 + perf_variation)))
            sorted_orgs.append(org)
            
        sorted_orgs = sorted(sorted_orgs, key=lambda x: x.calculated_score, reverse=True)[:5]
        
        top_performers = []
        for org in sorted_orgs:
            data = IncubatorOrgSerializer(org).data
            data['performance_score'] = org.calculated_score
            top_performers.append(data)

        return Response({
            'stats': {
                'total_orgs': total_orgs,
                'avg_performance': round(avg_perf, 1),
                'active_orgs': active_orgs,
                'weak_orgs': weak_orgs,
                'total_revenue': float(total_revenue),
                'total_orders': total_orders,
                'gallery_items': gallery_items
            },
            'top_performers': top_performers
        })

class IncubatorAnalyticsAPIView(APIView):
    permission_classes = [IsIncubatorPermission]

    def get(self, request):
        user = request.user
        orgs = User.objects.filter(incubator=user, role='INSTITUTION')
        org_ids = orgs.values_list('id', flat=True)
        
        period = request.GET.get('period', '12m')
        now = timezone.now()
        date_ranges = [] # list of (start_date, end_date, label)
        
        if period == '7d':
            for i in range(6, -1, -1):
                d = now - timedelta(days=i)
                start = d.replace(hour=0, minute=0, second=0)
                end = d.replace(hour=23, minute=59, second=59)
                date_ranges.append((start, end, d.strftime('%Y-%m-%d')))
        elif period == '30d':
            for i in range(29, -1, -1):
                d = now - timedelta(days=i)
                start = d.replace(hour=0, minute=0, second=0)
                end = d.replace(hour=23, minute=59, second=59)
                date_ranges.append((start, end, d.strftime('%m-%d')))
        else:
            num_months = 12 if period == '12m' else 6
            for i in range(num_months - 1, -1, -1):
                d = now - timedelta(days=i*30)
                year, m_val = d.year, d.month
                start = timezone.datetime(year, m_val, 1, tzinfo=now.tzinfo)
                if m_val == 12: end = timezone.datetime(year+1, 1, 1, tzinfo=now.tzinfo)
                else: end = timezone.datetime(year, m_val+1, 1, tzinfo=now.tzinfo)
                date_ranges.append((start, end, d.strftime('%Y-%m')))

        from apps.orders.models import OrderItem
        from django.db.models import Sum, F

        analytics_data = []
        for start_date, end_date, label in date_ranges:
            # نمو عدد المؤسسات
            count = User.objects.filter(
                incubator=user, 
                role='INSTITUTION', 
                date_joined__lte=end_date
            ).count()

            # عدد الطلبات في هذا المجال
            monthly_orders = OrderItem.objects.filter(
                Q(product__vendor_id__in=org_ids) | Q(service__vendor_id__in=org_ids),
                order__created_at__gte=start_date,
                order__created_at__lt=end_date
            ).values('order').distinct().count()

            # مبيعات المعارض في هذا المجال
            monthly_revenue = OrderItem.objects.filter(
                Q(product__vendor_id__in=org_ids) | Q(service__vendor_id__in=org_ids),
                order__created_at__gte=start_date,
                order__created_at__lt=end_date
            ).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0

            analytics_data.append({
                'label': label, 
                'total_orgs': count, 
                'revenue': float(monthly_revenue),
                'orders': monthly_orders
            })

        # بيانات أداء المؤسسات الكبرى (مقارنة الأداء بناءً على النشاط الحقيقي)
        performance_lines = []
        top_orgs = orgs.order_by('-performance_score')[:5]
        
        for org in top_orgs:
            history = []
            for start_date, end_date, label in date_ranges:
                # المبيعات الشهرية للمؤسسة المعنية
                monthly_revenue = OrderItem.objects.filter(
                    Q(product__vendor_id=org.id) | Q(service__vendor_id=org.id),
                    order__created_at__gte=start_date,
                    order__created_at__lt=end_date
                ).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
                
                # عدد طلبات المؤسسة الشهري
                monthly_orders = OrderItem.objects.filter(
                    Q(product__vendor_id=org.id) | Q(service__vendor_id=org.id),
                    order__created_at__gte=start_date,
                    order__created_at__lt=end_date
                ).values('order').distinct().count()
                
                # استنباط نسبة الأداء الحقيقية: المبيعات القوية والطلبات الكثيرة تزيد من الأداء
                perf_variation = min(50, int((monthly_revenue / 50000) * 30) + (monthly_orders * 2))
                
                # مزج الدرجة الأساسية مع النشاط الشهري للحصول على منحنى واقعي
                base_score = org.performance_score
                calculated_score = min(100, max(0, int(base_score * 0.5 + perf_variation)))
                
                history.append({'month': label, 'score': calculated_score})
            
            performance_lines.append({
                'name': org.first_name or org.username,
                'data': history
            })

        return Response({
            'growth': analytics_data,
            'performance_lines': performance_lines
        })

class OrganizationActionAPIView(APIView):
    permission_classes = [IsIncubatorPermission]

    def post(self, request, pk):
        action_type = request.data.get('action') # 'approved' or 'rejected'
        try:
            req = OrganizationRequest.objects.get(pk=pk, incubator=request.user)
        except OrganizationRequest.DoesNotExist:
            return Response({'error': 'الطلب غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        if action_type == 'approved':
            req.status = 'approved'
            req.save()
            
            # Create the institution user if it doesn't exist
            username = req.name.lower().replace(' ', '_')
            import uuid
            username = f"{username}_{uuid.uuid4().hex[:4]}"
            User.objects.create_user(
                username=username,
                password='admin_pass_2024', # generic password for new requests
                first_name=req.name,
                role='INSTITUTION',
                incubator=request.user,
                is_verified=True,
                performance_score=0
            )

            return Response({'message': 'تم قبول الطلب وإنشاء حساب المؤسسة بنجاح'})
        elif action_type == 'rejected':
            req.status = 'rejected'
            req.save()
            return Response({'message': 'تم رفض الطلب'})
        
        return Response({'error': 'إجراء غير صالح'}, status=status.HTTP_400_BAD_REQUEST)

class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer

    def get_queryset(self):
        return TeamMember.objects.filter(user=self.request.user)
