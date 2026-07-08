from django import forms
from .podmiot_model  import Podmiot

class PodmiotForm(forms.ModelForm):
    class Meta:
        model = Podmiot
        fields = ['kod', 'nazwa']
        widgets = {
            'kod': forms.TextInput(attrs={'class': 'form-control'}),
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
        }
