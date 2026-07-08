import ast
from django import forms
from fossa2.components.slownik.slownik_model import Slownik

class SlownikForm(forms.ModelForm):
    opcje = forms.CharField(
        widget=forms.Textarea()
    )

    class Meta:
        model = Slownik
        fields = ['nazwa', 'opcje']

    def clean_nazwa(self):
        nazwa = self.cleaned_data.get('nazwa')

        if Slownik.objects.filter(nazwa=nazwa).exists():
            raise forms.ValidationError(f"Słownik o nazwie '{nazwa}' już istnieje!")

        return nazwa
    def clean_opcje(self):
        data = self.cleaned_data['opcje']
        try:

            converted_data = ast.literal_eval(data)

            if not isinstance(converted_data, list):
                raise forms.ValidationError("Niepoprawny format listy. Wpisz np: ['TAK', 'NIE']")

            return converted_data
        except (ValueError, SyntaxError):
            raise forms.ValidationError("Niepoprawny format listy. Wpisz np: ['TAK', 'NIE']")