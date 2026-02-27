from django import forms
from .models import Product, Batch, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'is_active']

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['product', 'batch_number', 'expiry_date', 'stock']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']