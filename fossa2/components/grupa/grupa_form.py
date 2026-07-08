from django import forms
from fossa2.components.grupa.grupa_model import GrupaNaglowek

class GrupaNaglowekForm(forms.ModelForm):
    class Meta:
        model = GrupaNaglowek
        fields = ['nazwa']
        widgets = {
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
        }