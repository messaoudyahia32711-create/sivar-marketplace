# apps/reviews/urls.py

from django.urls import path
from apps.reviews.views import (
    ReviewListView,
    CreateReviewView,
    UserReviewsView,
)

app_name = 'reviews'

urlpatterns = [
    # GET  /api/reviews/?product_id=3
    path('', ReviewListView.as_view(), name='review-list'),

    # POST /api/reviews/create/
    path('create/', CreateReviewView.as_view(), name='review-create'),

    # GET  /api/reviews/me/
    path('me/', UserReviewsView.as_view(), name='user-reviews'),
]