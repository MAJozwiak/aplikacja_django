from django import forms
from .ankieta_model import AnkietaNaglowek

class AnkietaNaglowekForm(forms.ModelForm):
    class Meta:
        model = AnkietaNaglowek
        fields = ['nazwa', 'id_grupa', 'id_obszar']
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'id_grupa': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'id_obszar': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
        }