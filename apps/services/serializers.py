from rest_framework import serializers
from .models import Service, ServiceCategory, ServiceImage

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug']

class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ['id', 'image', 'alt_text', 'order']

class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_username = serializers.CharField(source='vendor.username', read_only=True)
    vendor_name = serializers.SerializerMethodField()
    images = ServiceImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'price', 'category', 'category_name',
            'vendor_username', 'vendor_name',
            'wilayas', 'image_main', 'duration_hours', 'is_active',
            'images', 'uploaded_images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        wilayas = validated_data.pop('wilayas', [])
        service = Service.objects.create(**validated_data)
        service.wilayas.set(wilayas)
        
        for image_data in uploaded_images:
            ServiceImage.objects.create(service=service, image=image_data)
        
        return service

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        wilayas = validated_data.pop('wilayas', [])
        if wilayas:
            instance.wilayas.set(wilayas)
            
        instance = super().update(instance, validated_data)
        
        for image_data in uploaded_images:
            ServiceImage.objects.create(service=instance, image=image_data)
            
        return instance

    def get_vendor_name(self, obj) -> str:
        if not obj.vendor:
            return "مجهول"
        full_name = obj.vendor.get_full_name()
        return full_name.strip() or obj.vendor.username