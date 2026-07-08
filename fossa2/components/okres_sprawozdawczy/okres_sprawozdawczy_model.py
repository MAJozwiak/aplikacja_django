from django.db import models

class OkresSprawozdawczy(models.Model):
    rok = models.IntegerField(unique=True, verbose_name="Rok sprawozdawczy")
    czy_zamrozony = models.BooleanField(default=False, verbose_name="Czy opublikowany/zamrożony?")

    class Meta:
        ordering = ['-rok']

    def __str__(self):
        status = "Zamrożony" if self.czy_zamrozony else "Otwarty"
        return f"{self.rok} ({status})"

    @classmethod
    def get_aktywny_rok(cls):
        return cls.objects.filter(czy_zamrozony=False).first()

    def zamroz_i_utworz_kolejny(self):
        self.czy_zamrozony = True
        self.save()

        nowy_rok = OkresSprawozdawczy.objects.create(
            rok=self.rok + 1,
            czy_zamrozony=False
        )
        return nowy_rok

