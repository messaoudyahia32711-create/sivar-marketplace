from rest_framework import serializers
from .models import Wilaya, Commune


class CommuneSerializer(serializers.ModelSerializer):
    """متسلسل البلديات (بيانات أساسية فقط)"""
    class Meta:
        model = Commune
        fields = ['id', 'name']


class WilayaSerializer(serializers.ModelSerializer):
    """متسلسل الولايات مع إمكانية إظهار البلديات التابعة لها"""
    
    # لعرض البلديات داخل كل ولاية (اختياري)
    communes = CommuneSerializer(many=True, read_only=True)

    class Meta:
        model = Wilaya
        fields = ['id', 'name', 'code', 'shipping_cost', 'communes']