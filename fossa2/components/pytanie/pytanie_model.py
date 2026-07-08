from django.db import models
from fossa2.components.podblok.podblok_model import Podblok

class Pytanie(models.Model):
    id_podbloku = models.ForeignKey(Podblok, on_delete=models.CASCADE, related_name='pytania')
    kod = models.CharField(max_length=20, unique=False)
    tresc = models.CharField(max_length=700)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)
    data_od = models.DateField()
    data_do = models.DateField()

    def __str__(self):
        return f"{self.kod} - {self.tresc[:50]}"

    def czy_z_biezacego_roku(self, rok):
        return self.data_od.year == rok