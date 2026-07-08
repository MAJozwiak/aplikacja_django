from django.db import models
from datetime import date
from fossa2.config import INFINITY_DATE
from fossa2.components.grupa.grupa_model import GrupaNaglowek
from fossa2.components.podmiot.podmiot_model import Podmiot

class GrupaPodmioty(models.Model):
    id_grupa = models.ForeignKey(GrupaNaglowek, on_delete=models.CASCADE)
    id_podmiotu = models.ForeignKey(Podmiot, on_delete=models.SET_NULL, null=True, blank=True)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)
    data_od = models.DateField(default=date.today)
    data_do = models.DateField(default=INFINITY_DATE)
    nazwa_podmiotu_snapshot = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.id_podmiotu}"

    class Meta:
        ordering = ["id_podmiotu"]