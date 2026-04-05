from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views, incubator_api
from apps.chat import views as chat_views

app_name = 'vendors'

# ── Router للـ ViewSets ──────────────────────────────────────────
router = DefaultRouter()
router.register(r'products', api_views.VendorProductViewSet, basename='vendor-product')
router.register(r'services', api_views.VendorServiceViewSet, basename='vendor-service')
router.register(r'coupons', api_views.CouponViewSet, basename='vendor-coupon')
router.register(r'team', incubator_api.TeamViewSet, basename='team')
router.register(r'organizations', incubator_api.IncubatorOrganizationsViewSet, basename='incubator-organizations')
router.register(r'incubator/team', incubator_api.TeamViewSet, basename='incubator-team') # Keep old for now
router.register(r'incubator/organization-requests', incubator_api.OrganizationRequestViewSet, basename='incubator-org-request')

# ── URL patterns ─────────────────────────────────────────────────
urlpatterns = [

    # ── Template Views (القديمة — يمكن حذفها لاحقاً) ──
    path('login/',    views.vendor_login,    name='login'),
    path('logout/',   views.vendor_logout,   name='logout'),
    path('dashboard/', views.vendor_dashboard, name='dashboard'),

    # ── API: Dashboard ──
    path('api/dashboard/',
         api_views.DashboardOverviewAPIView.as_view(),
         name='api-dashboard'),

    # ── API: Analytics ──
    path('api/analytics/revenue/',
         api_views.RevenueAnalyticsAPIView.as_view(),
         name='api-revenue'),
    path('api/analytics/top-products/',
         api_views.VendorTopProductsAPIView.as_view(),
         name='api-top-products'),

    # ── API: Orders ──
    path('api/orders/',
         api_views.VendorOrderListView.as_view(),
         name='api-orders'),
    path('api/orders/pending-count/',
         api_views.VendorPendingOrdersCountView.as_view(),
         name='api-orders-pending-count'),
    path('api/orders/<int:pk>/status/',
         api_views.VendorOrderStatusUpdateView.as_view(),
         name='api-order-status'),

    # ── API: Products (عبر Router) ──
    path('api/', include(router.urls)),

    # ── API: Reviews ──
    path('api/reviews/',
         api_views.VendorReviewListView.as_view(),
         name='api-reviews'),

    # ── API: Store ──
    path('api/store/',
         api_views.VendorStoreAPIView.as_view(),
         name='api-store'),

    # ── API: Incubator Specialized ──
    path('api/incubator/stats/', 
         incubator_api.IncubatorDashboardStatsAPIView.as_view(), 
         name='api-incubator-stats'),
    path('api/incubator/analytics/', 
         incubator_api.IncubatorAnalyticsAPIView.as_view(), 
         name='api-incubator-analytics'),
    path('api/incubator/org-action/<int:pk>/', 
         incubator_api.OrganizationActionAPIView.as_view(), 
         name='api-incubator-org-action'),

    # ── API: Incubator Chats (Bridged from Chat App) ──
    path('api/incubator/chats/', 
         chat_views.ConversationListView.as_view(), 
         name='api-incubator-chats'),
    path('api/incubator/chats/<int:pk>/messages/', 
         chat_views.ConversationDetailView.as_view(), 
         name='api-incubator-chat-messages'),

    # ── API: Public Store (عامة - بدون مصادقة) ──
    path('api/public/store/<str:username>/',
         api_views.PublicStoreAPIView.as_view(),
         name='api-public-store'),

    # ── API: Homepage (الصفحة الرئيسية العامة) ──
    path('api/public/homepage/',
         api_views.HomepageAPIView.as_view(),
         name='api-homepage'),

    # ── API: Chat Bridge (لجميع لوحات التحكم) ──
    path('api/chat/conversations/',
         chat_views.ConversationListView.as_view(),
         name='api-chat-conversations'),
    path('api/chat/conversations/<int:pk>/',
         chat_views.ConversationDetailView.as_view(),
         name='api-chat-conversation-detail'),
    path('api/chat/messages/send/',
         chat_views.SendMessageView.as_view(),
         name='api-chat-send-message'),
]