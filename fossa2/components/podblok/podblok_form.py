from django import forms
from fossa2.components.podblok.podblok_model import Podblok
from fossa2.components.blok.blok_model import Blok
from fossa2.components.obszar.obszar_model import Obszar

class PodblokForm(forms.ModelForm):
    id_obszaru = forms.ModelChoiceField(
        queryset=Obszar.objects.all(),
        label="Obszar",
        widget=forms.Select(attrs={'id': 'id_obszaru_select', 'class': 'form-control'})
    )

    class Meta:
        model = Podblok
        fields = ['id_obszaru', 'id_bloku', 'tresc']
        widgets = {
            'id_bloku': forms.Select(attrs={'id': 'id_bloku_select', 'class': 'form-control'}),
            'tresc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_bloku'].queryset = Blok.objects.none()

        if 'id_obszaru' in self.data:
            try:
                obszar_id = int(self.data.get('id_obszaru'))
                self.fields['id_bloku'].queryset = Blok.objects.filter(id_obszaru_id=obszar_id)
            except (ValueError, TypeError):
                pass

        if self.instance.pk and self.instance.id_bloku:
            self.fields['id_bloku'].queryset = self.instance.id_bloku.id_obszaru.bloki.all()