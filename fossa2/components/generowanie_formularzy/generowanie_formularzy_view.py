import os
import io
import zipfile
import shutil
from datetime import date
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.components.grupa.grupa_model import GrupaNaglowek
from fossa2.generator import get_data_by_grupanaglowek_id, transform_dict, generuj
from fossa2.config import GENEROWANIE_TEMPLATE

class GenerowanieFormularzyView(View):
    template_name = GENEROWANIE_TEMPLATE
    folder_raportow = os.path.join(os.getcwd(), 'fossa2', 'generated_reports')

    def get_daty_okresu(self):
        najnowszy_okres = OkresSprawozdawczy.objects.order_by('-rok').first()
        rok = najnowszy_okres.rok if najnowszy_okres else date.today().year
        poczatek_roku = date(rok, 1, 1)
        koniec_roku = date(rok, 12, 31)
        return poczatek_roku, koniec_roku

    def wyczysc_lub_utworz_folder_raportow(self):
        if os.path.exists(self.folder_raportow):
            for plik in os.listdir(self.folder_raportow):
                sciezka_pliku = os.path.join(self.folder_raportow, plik)
                try:
                    if os.path.isfile(sciezka_pliku) or os.path.islink(sciezka_pliku):
                        os.unlink(sciezka_pliku)
                    elif os.path.isdir(sciezka_pliku):
                        shutil.rmtree(sciezka_pliku)
                except Exception as e:
                    print(f'Błąd podczas usuwania {sciezka_pliku}: {e}')
        else:
            os.makedirs(self.folder_raportow)

    def handle_generuj_raporty(self, request, poczatek_roku, koniec_roku):
        self.wyczysc_lub_utworz_folder_raportow()

        grupanaglowek_id = request.POST.get('grupanaglowek_id')
        print("y")

        data = get_data_by_grupanaglowek_id(grupanaglowek_id, poczatek_roku, koniec_roku)
        podmioty = data['podmioty']
        ankiety = data['ankiety']

        for ankieta in ankiety:
            paczka_jedna_ankieta = {
                'ankiety': [ankieta],
                'podmioty': podmioty,
                'grupa_naglowek': data['grupa_naglowek']
            }
            transformed = transform_dict(paczka_jedna_ankieta)
            hierarchia = transformed['hierarchia']

            for podmiot in podmioty:
                generuj(hierarchia, podmiot, ankieta['nazwa'])

    def handle_pobierz_zip(self):
        if not os.path.exists(self.folder_raportow):
            return HttpResponse("Folder z raportami nie istnieje na serwerze.")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            pliki = os.listdir(self.folder_raportow)

            for nazwa_pliku in pliki:
                sciezka_pelna = os.path.join(self.folder_raportow, nazwa_pliku)
                if os.path.isfile(sciezka_pelna):
                    zip_file.write(sciezka_pelna, arcname=nazwa_pliku)

        buffer.seek(0)
        if buffer.getbuffer().nbytes == 0:
            return HttpResponse("Folder jest pusty, nie ma czego pobrać.")

        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="wszystkie_raporty.zip"'
        return response

    def renderuj_widok(self, request, poczatek_roku, koniec_roku):
        grupanagloweks = GrupaNaglowek.objects.filter(
            data_od__lte=koniec_roku,
            data_do__gte=poczatek_roku
        )
        return render(request, self.template_name, {'grupanagloweks': grupanagloweks})

    def get(self, request, *args, **kwargs):
        poczatek_roku, koniec_roku = self.get_daty_okresu()
        print("x")
        return self.renderuj_widok(request, poczatek_roku, koniec_roku)

    def post(self, request, *args, **kwargs):
        poczatek_roku, koniec_roku = self.get_daty_okresu()
        print("x")

        if 'generuj' in request.POST:
            self.handle_generuj_raporty(request, poczatek_roku, koniec_roku)

        if 'akcja' in request.POST:
            response = self.handle_pobierz_zip()
            if response:
                return response

        return self.renderuj_widok(request, poczatek_roku, koniec_roku)
