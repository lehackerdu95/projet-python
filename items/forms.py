"""
Forms for the items application.
"""

from django import forms
from .models import Collection, Item


class CollectionForm(forms.ModelForm):
    """Form for creating and updating collections."""
    
    class Meta:
        model = Collection
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Collection name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description (optional)',
                'rows': 4
            }),
        }


class ItemForm(forms.ModelForm):
    """Form for creating and updating items."""
    
    class Meta:
        model = Item
        fields = ['name', 'description', 'value', 'acquisition_date', 'condition', 'image', 'is_for_sale', 'sale_price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Item name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description (optional)',
                'rows': 4
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'acquisition_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'condition': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_for_sale': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sale price (if for sale)',
                'step': '0.01'
            }),
        }
