# apps/cart/urls.py

from django.urls import path
from .views import (
    CartDetailView,
    AddToCartView,
    CartItemDetailView,
    ClearCartView,
)

app_name = 'cart'

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart-detail'),
    path('add/', AddToCartView.as_view(), name='cart-add'),
    path('item/<int:item_id>/', CartItemDetailView.as_view(), name='cart-item'),
    path('clear/', ClearCartView.as_view(), name='cart-clear'),
]