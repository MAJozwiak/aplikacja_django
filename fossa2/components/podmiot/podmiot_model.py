from django.db import models
from fossa2.config import PODMIOT_KOD_MAX, PODMIOT_NAZWA_MAX


class Podmiot(models.Model):
    kod = models.CharField(max_length=PODMIOT_KOD_MAX, unique=True)
    nazwa = models.CharField(max_length=PODMIOT_NAZWA_MAX)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.kod}"

    class Meta:
        ordering = ["kod"]
