from fossa2.components.podblok.podblok_model import Podblok
from fossa2.components.pytanie.pytanie_model import Pytanie
from fossa2.components.blok.blok_model import Blok
from fossa2.components.obszar.obszar_model import Obszar
from django import forms


class PytanieForm(forms.ModelForm):
    id_obszaru = forms.ModelChoiceField(
        queryset=Obszar.objects.all(),
        label="Obszar",
        widget=forms.Select(attrs={'id': 'id_obszaru_select', 'class': 'form-control'})
    )

    id_bloku = forms.ModelChoiceField(
        queryset=Blok.objects.all(),
        label="Blok",
        widget=forms.Select(attrs={'id': 'id_bloku_select', 'class': 'form-control'})
    )

    class Meta:
        model = Pytanie
        fields = ['id_obszaru', 'id_bloku', 'id_podbloku', 'tresc']
        widgets = {
            'id_podbloku': forms.Select(attrs={'id': 'id_podbloku_select', 'class': 'form-control'}),
            'tresc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['id_bloku'].queryset = Blok.objects.none()
        self.fields['id_podbloku'].queryset = Podblok.objects.none()

        if 'id_obszaru' in self.data:
            try:
                area_id = int(self.data.get('id_obszaru'))
                self.fields['id_bloku'].queryset = Blok.objects.filter(id_obszaru_id=area_id)
            except (ValueError, TypeError):
                pass

        if 'id_bloku' in self.data:
            try:
                block_id = int(self.data.get('id_bloku'))
                self.fields['id_podbloku'].queryset = Podblok.objects.filter(id_bloku_id=block_id)
            except (ValueError, TypeError):
                pass