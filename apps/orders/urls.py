from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # POST   /api/orders/create/       → إنشاء طلب جديد
    path(
        'create/',
        views.OrderCreateView.as_view(),
        name='order-create',
    ),

    # GET    /api/orders/              → قائمة طلباتي
    path(
        '',
        views.OrderListView.as_view(),
        name='order-list',
    ),

    # GET    /api/orders/<order_id>/   → تفاصيل طلب
    path(
        '<int:order_id>/',
        views.OrderDetailView.as_view(),
        name='order-detail',
    ),
]