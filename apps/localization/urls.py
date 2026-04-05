from django.urls import path
from .views import WilayaListView, CommuneListView

app_name = 'localization'

urlpatterns = [
    path('wilayas/', WilayaListView.as_view(), name='wilaya-list'),
    path('communes/', CommuneListView.as_view(), name='commune-list'),
]