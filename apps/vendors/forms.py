from django import forms
from apps.products.models import Product


class ProductForm(forms.ModelForm):
    """
    نموذج إضافة/تعديل المنتجات — مخصص للتجار فقط.
    الحقول الحساسة (vendor, slug, created_at, updated_at) مخفية تماماً.
    """

    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'brand',
            'price',
            'stock',
            'image_main',
            'is_active',
            'description',
        ]

        # -------- التسميات العربية --------
        labels = {
            'name':        'اسم المنتج',
            'category':    'التصنيف',
            'brand':       'العلامة التجارية',
            'price':       'السعر',
            'stock':       'الكمية المتوفرة',
            'image_main':   'صورة المنتج',
            'is_active':   'نشط (معروض للبيع)',
            'description': 'وصف المنتج',
        }

        # -------- Widgets مع Bootstrap 5 --------
        widgets = {
            'name': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'أدخل اسم المنتج',
            }),

            'category': forms.Select(attrs={
                'class': 'form-select',
            }),

            'brand': forms.Select(attrs={
                'class': 'form-select',
            }),

            'price': forms.NumberInput(attrs={
                'class':       'form-control',
                'placeholder': '0.00',
                'min':         '0',
                'step':        '0.01',
            }),

            'stock': forms.NumberInput(attrs={
                'class':       'form-control',
                'placeholder': '0',
                'min':         '0',
            }),

            'image_main': forms.ClearableFileInput(attrs={
                'class':  'form-control',
                'accept': 'image/*',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),

            'description': forms.Textarea(attrs={
                'class':       'form-control',
                'placeholder': 'أدخل وصفاً تفصيلياً للمنتج...',
                'rows':        5,
            }),
        }

    # -------- تنظيفات مخصّصة --------
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('السعر يجب أن يكون أكبر من صفر.')
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('الكمية لا يمكن أن تكون سالبة.')
        return stock

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 3:
            raise forms.ValidationError('اسم المنتج يجب أن يكون 3 أحرف على الأقل.')
        return name