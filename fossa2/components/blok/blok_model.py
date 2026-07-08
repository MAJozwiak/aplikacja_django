from django.db import models
from datetime import date
from fossa2.config import INFINITY_DATE
from django.db.models.functions import Length

class BlokManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by(Length('kod').asc(), 'kod', '-data_od')
class Blok(models.Model):
    id_obszaru = models.ForeignKey('Obszar', on_delete=models.CASCADE, related_name='bloki')
    kod = models.CharField(max_length=20, unique=False)
    tresc = models.CharField(max_length=300)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)
    data_od = models.DateField(default=date.today)
    data_do = models.DateField(default=INFINITY_DATE)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    objects = BlokManager()


    def __str__(self):
        return f"{self.kod} - {self.tresc[:30]}"

    class Meta:
        ordering = ["kod", "-data_od"]

    def czy_z_biezacego_roku(self, rok_sprawozdawczy):
        return self.data_od.year == rok_sprawozdawczy

