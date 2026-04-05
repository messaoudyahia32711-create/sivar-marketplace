from django.contrib import admin
from .models import Service, ServiceCategory

class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'wilayas', 'created_at')
    search_fields = ('name', 'description', 'vendor__username')
    raw_id_fields = ('vendor',)
    filter_horizontal = ('wilayas',)
    list_editable = ('price', 'is_active')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('vendor', 'category', 'name', 'description')
        }),
        ('التسعير والتفاصيل', {
            'fields': ('price', 'duration_hours', 'image_main')
        }),
        ('التغطية والحالة', {
            'fields': ('wilayas', 'is_active')
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(Service, ServiceAdmin)
