from django.db import models
from datetime import date
from fossa2.components.blok.blok_model import Blok
from fossa2.config import INFINITY_DATE


class Podblok(models.Model):
    id_bloku = models.ForeignKey(Blok, on_delete=models.CASCADE, related_name='podbloki')
    kod = models.CharField(max_length=20, unique=False)
    tresc = models.CharField(max_length=300)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)
    data_od = models.DateField(default=date.today)
    data_do = models.DateField(default=INFINITY_DATE)
    data_utworzenia = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.kod}"

    class Meta:
        ordering = ["kod"]

    def czy_z_biezacego_roku(self, rok_sprawozdawczy):
        return self.data_od.year == rok_sprawozdawczy