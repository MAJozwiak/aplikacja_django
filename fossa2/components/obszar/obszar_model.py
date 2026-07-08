from django.db import models

class Obszar(models.Model):
    kod = models.CharField(max_length=10, unique=True)
    nazwa = models.CharField(max_length=100, unique=True)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    utworzone_przez_uzytkownika = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.kod}"

    class Meta:
        ordering = ["kod"]