from django.db import models
from fossa2.components.pytanie.pytanie_model import Pytanie
from fossa2.components.slownik.slownik_model import Slownik

class Podzapytanie(models.Model):
    id_pytania = models.ForeignKey(Pytanie, on_delete=models.CASCADE, related_name='podzapytania')
    kod = models.CharField(max_length=20, unique=False)
    tresc = models.CharField(max_length=700)
    obligatoryjne = models.BooleanField(default=True)
    wytyczne = models.CharField(max_length=700)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)
    data_od = models.DateField()
    data_do = models.DateField()
    slownik = models.ForeignKey(
        Slownik,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='podzapytania'
    )
    def __str__(self):
        return self.kod

    class Meta:
        ordering = ["kod"]

    def czy_z_biezacego_roku(self, rok):
        return self.data_od.year == rok

    def is_valid(self):
        pass
