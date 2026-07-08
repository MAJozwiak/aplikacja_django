from django.db import models
from datetime import date
from fossa2.config import INFINITY_DATE

class GrupaNaglowek(models.Model):
    nazwa = models.CharField(max_length=255, unique=True)
    data_utworzenia = models.DateField(auto_now_add=True)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)
    data_od = models.DateField(default=date.today)
    data_do = models.DateField(default=INFINITY_DATE)


    def __str__(self):
        return self.nazwa

    class Meta:
        ordering = ["nazwa"]

