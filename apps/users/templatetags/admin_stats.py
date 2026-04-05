from django import template
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.services.models import Service
from apps.cart.models import Cart

register = template.Library()

@register.inclusion_tag('admin/includes/stats_cards.html')
def admin_dashboard_stats():
    User = get_user_model()
    return {
        'users_count': User.objects.count(),
        'products_count': Product.objects.count(),
        'services_count': Service.objects.count(),
        'carts_count': Cart.objects.count(),
    }
