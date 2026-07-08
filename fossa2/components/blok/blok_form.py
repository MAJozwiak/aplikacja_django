from django import forms
from fossa2.components.blok.blok_model import Blok


class BlokForm(forms.ModelForm):
    class Meta:
        model = Blok
        fields = ['id_obszaru', 'tresc']
        widgets = {
            'id_obszaru': forms.Select(attrs={'class': 'form-control'}),
            'tresc': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }