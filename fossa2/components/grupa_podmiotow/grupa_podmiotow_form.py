from .grupa_podmiotow_model import GrupaPodmioty
from django import forms

class GrupaPodmiotyForm(forms.ModelForm):
    class Meta:
        model = GrupaPodmioty
        fields = ['id_grupa']
        widgets = {
            'id_grupa': forms.Select(attrs={'class': 'form-control'}),
        }