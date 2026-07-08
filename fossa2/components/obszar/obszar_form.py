from django import forms

from .obszar_model import Obszar


class ObszarForm(forms.ModelForm):
    class Meta:
        model = Obszar
        fields = ['kod', 'nazwa']
        widgets = {
            'kod': forms.TextInput(attrs={'class': 'form-control'}),
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_kod(self):
        kod = self.cleaned_data.get('kod').strip().upper()

        # Sprawdzamy czy kod już istnieje (wykluczając obecny obiekt przy edycji)
        if Obszar.objects.filter(kod__iexact=kod).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f"Obszar z kodem '{kod}' już istnieje!")

        return kod
    def clean_nazwa(self):
        nazwa = self.cleaned_data.get('nazwa').strip()

        # Sprawdzamy czy nazwa już istnieje (ignorując wielkość liter)
        if Obszar.objects.filter(nazwa__iexact=nazwa).exists():
            raise forms.ValidationError(f"Obszar o nazwie '{nazwa}' już istnieje!")

        return nazwa