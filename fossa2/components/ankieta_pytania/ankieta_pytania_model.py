from django.db import models
from fossa2.components.ankieta.ankieta_model import AnkietaNaglowek
from fossa2.components.podzapytanie.podzapytanie_model import Podzapytanie

class AnkietaPytania(models.Model):
    id_ankieta_naglowek = models.ForeignKey(AnkietaNaglowek, on_delete=models.CASCADE)
    id_podzapytania = models.ForeignKey(Podzapytanie, on_delete=models.CASCADE)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.id_ankieta_naglowek} - {self.id_podzapytania}"

    class Meta:
        ordering = ["id_ankieta_naglowek", "id_podzapytania"]