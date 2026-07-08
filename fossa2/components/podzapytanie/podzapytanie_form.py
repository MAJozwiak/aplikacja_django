from django import forms
from fossa2.components.slownik.slownik_model import Slownik
from fossa2.components.podzapytanie.podzapytanie_model import Podzapytanie
from fossa2.components.blok.blok_model import Blok
from fossa2.components.podblok.podblok_model import Podblok
from fossa2.components.pytanie.pytanie_model import Pytanie
from fossa2.components.obszar.obszar_model import Obszar

class PodzapytanieForm(forms.ModelForm):
    id_obszaru = forms.ModelChoiceField(
        queryset=Obszar.objects.all(),
        label="Obszar",
        required=False,
        widget=forms.Select(attrs={'id': 'id_obszaru_select', 'class': 'form-control'})
    )

    id_bloku = forms.ModelChoiceField(
        queryset=Blok.objects.none(),
        label="Blok",
        required=False,
        widget=forms.Select(attrs={'id': 'id_bloku_select', 'class': 'form-control'})
    )

    id_podbloku = forms.ModelChoiceField(
        queryset=Podblok.objects.none(),
        label="Podblok",
        required=False,
        widget=forms.Select(attrs={'id': 'id_podbloku_select', 'class': 'form-control'})
    )
    slowniki = forms.ModelChoiceField(
        queryset=Slownik.objects.all(),
        empty_label="--- Wybierz słownik ---",
        required=False,
        label="Słownik"
    )
    class Meta:
        model = Podzapytanie
        fields = ['id_obszaru', 'id_bloku', 'id_podbloku', 'id_pytania', 'tresc', 'obligatoryjne', 'wytyczne', 'slownik']
        widgets = {
            'id_pytania': forms.Select(attrs={'id': 'id_pytania_select', 'class': 'form-control'}),
            'tresc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'style': 'resize: none;'}),
            'obligatoryjne': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wytyczne': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['id_bloku'].queryset = Blok.objects.none()
        self.fields['id_podbloku'].queryset = Podblok.objects.none()
        self.fields['id_pytania'].queryset = Pytanie.objects.none()

        data = self.data

        if 'id_obszaru' in data:
            try:
                area_id = int(data.get('id_obszaru'))
                self.fields['id_bloku'].queryset = Blok.objects.filter(id_obszaru_id=area_id)
            except (ValueError, TypeError):
                pass

        if 'id_bloku' in data:
            try:
                block_id = int(data.get('id_bloku'))
                self.fields['id_podbloku'].queryset = Podblok.objects.filter(id_bloku_id=block_id)
            except (ValueError, TypeError):
                pass

        if 'id_podbloku' in data:
            try:
                podblock_id = int(data.get('id_podbloku'))
                self.fields['id_pytania'].queryset = Pytanie.objects.filter(id_podbloku_id=podblock_id)
            except (ValueError, TypeError):
                pass