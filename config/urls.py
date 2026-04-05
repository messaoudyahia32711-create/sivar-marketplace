from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from apps.products.views import home_view, catalog_view
from apps.users.views import login_page_view, register_page_view, dashboard_redirect_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── API Routes ─────────────────────────────────────────────────
    path('api/users/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/localization/', include('apps.localization.urls')),
    path('api/vendors/', include('apps.vendors.urls')),
    path('api/chat/', include('apps.chat.urls')),

    # ── Projects Apps Routes (Templates) ──────────
    path('', home_view, name='home'),
    path('catalog/', catalog_view, name='catalog'),
    path('login/', login_page_view, name='login'),
    path('register/', register_page_view, name='register'),
    path('dashboard-redirect/', dashboard_redirect_view, name='dashboard-redirect'),
]

# ── خدمة ملفات الوسائط أثناء التطوير ──────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)