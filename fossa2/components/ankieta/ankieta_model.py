from django.db import models
from datetime import date
from fossa2.components.grupa.grupa_model import GrupaNaglowek
from fossa2.components.obszar.obszar_model import Obszar
from fossa2.config import INFINITY_DATE


class AnkietaNaglowek(models.Model):
    nazwa = models.CharField(max_length=100, unique=True)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    id_grupa = models.ForeignKey(GrupaNaglowek, on_delete=models.CASCADE)
    id_obszar = models.ForeignKey(Obszar , on_delete=models.SET_NULL, null=True, blank=True)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)
    data_od = models.DateField(default=date.today)
    data_do = models.DateField(default=INFINITY_DATE)
    kod_obszaru_snapshot = models.CharField(max_length=10)

    def __str__(self):
        return self.nazwa

    class Meta:
        ordering = ["nazwa"]

