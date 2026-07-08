from django import forms
from .ankieta_pytania_model import AnkietaPytania


class AnkietaPytaniaForm(forms.ModelForm):
    class Meta:
        model = AnkietaPytania
        fields = ['id_ankieta_naglowek']
        widgets = {
            'id_ankieta_naglowek': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }