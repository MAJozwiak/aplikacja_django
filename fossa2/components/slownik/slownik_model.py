from django.db import models

class Slownik(models.Model):
    nazwa = models.CharField(max_length=100,unique=True)
    opcje = models.JSONField()

    def __str__(self):
        return self.nazwa