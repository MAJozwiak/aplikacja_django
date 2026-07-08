from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from datetime import date
from fossa2.config import BLOK_TEMPLATE
from fossa2.components.podzapytanie.podzapytanie_model import Podzapytanie
from fossa2.components.pytanie.pytanie_model import Pytanie
from fossa2.components.blok.blok_form import BlokForm
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.config import INFINITY_DATE
from fossa2.components.podblok.podblok_model import Podblok
from fossa2.components.blok.blok_model import Blok


class BlokListView(View):
    template_name = BLOK_TEMPLATE
    success_url = None

    def dispatch(self, request, *args, **kwargs):
        self.success_url = request.META.get('HTTP_REFERER', request.path_info)
        return super().dispatch(request, *args, **kwargs)

    def load_okresy(self):
        return OkresSprawozdawczy.objects.all()

    def load_okres_context(self, request):
        rok_param = request.GET.get('rok')

        if rok_param:
            wybrany_okres = get_object_or_404(OkresSprawozdawczy, rok=int(rok_param))
        else:
            wybrany_okres = OkresSprawozdawczy.get_aktywny_rok()

        # zapisujemy do sejsji, aby wykorzystać w POST
        request.session['czy_tryb_edycji'] = bool(wybrany_okres and not wybrany_okres.czy_zamrozony)
        request.session['wybrany_okres'] = wybrany_okres.rok

        poczatek_roku = date(request.session['wybrany_okres'], 1, 1)
        koniec_roku = date(request.session['wybrany_okres'], 12, 31)

        return poczatek_roku, koniec_roku

    def okresy_exists(self, request, okresy_wszystkie):

        id_obszaru = request.GET.get('id_obszaru', '')
        kod = request.GET.get('kod', '')
        tresc = request.GET.get('tresc', '')

        results_per_page = int(request.GET.get('results_per_page', 25))

        poczatek_roku, koniec_roku = self.load_okres_context(request)

        queryset = Blok.objects.filter(
            data_od__lte=koniec_roku,
            data_do__gte=poczatek_roku
        )

        if id_obszaru:
            queryset = queryset.filter(id_obszaru__kod__icontains=id_obszaru)
        if kod:
            queryset = queryset.filter(kod__icontains=kod)
        if tresc:
            queryset = queryset.filter(tresc__icontains=tresc)

        paginator = Paginator(queryset, results_per_page)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'form': BlokForm(),
            'id_obszaru_filter': id_obszaru,
            'kod_filter': kod,
            'tresc_filter': tresc,
            'results_per_page': results_per_page,
            'okresy_wszystkie': okresy_wszystkie,
            'wybrany_okres': request.session['wybrany_okres'],
            'czy_tryb_edycji': request.session['czy_tryb_edycji'],
        }
        return render(request, self.template_name, context)

    def okresy_not_exists(self, request):
        return render(request, self.template_name, {'brak_danych': True})

    def list_bloki(self, request, extra_context=None):
        okresy_wszystkie = self.load_okresy()

        if okresy_wszystkie.exists():
            return self.okresy_exists(request, okresy_wszystkie)
        else:
            return self.okresy_not_exists(request)

    def generate_next_code(self, obszar):
        ostatnie = obszar.bloki.filter(data_do=INFINITY_DATE)

        if ostatnie.exists():
            kody = [int(b.kod) for b in ostatnie if b.kod.isdigit()]
            return str(max(kody) + 1) if kody else "1"

        return "1"

    def handle_add_blok(self, request):
        form = BlokForm(request.POST)
        if form.is_valid():
            blok = form.save(commit=False)
            blok.kod = self.generate_next_code(blok.id_obszaru)
            blok.utworzone_przez_uzytkownika = request.user.username
            blok.data_od = date(request.session['wybrany_okres'], 1, 1)
            blok.data_do = INFINITY_DATE
            blok.save()
        else:
            print("zadanie dodac message")


    def handle_delete_blok(self, request):
        blok_id = request.POST.get('blok_id')
        if blok_id:
            blok = get_object_or_404(Blok, id=blok_id)

            # jesli bieżący rok usuwamy kaskadowo
            if blok.czy_z_biezacego_roku(request.session['wybrany_okres']):
                blok.delete()



    def archiwe_components(selfself, request, blok, nowa_tresc):
        koniec_zeszlego_roku = date(request.session['wybrany_okres'] - 1, 12, 31)
        poczatek_tego_roku = date(request.session['wybrany_okres'], 1, 1)

        blok_archiwalny = Blok.objects.create(
            id_obszaru=blok.id_obszaru,
            kod=blok.kod,
            tresc=blok.tresc,
            utworzone_przez_uzytkownika=blok.utworzone_przez_uzytkownika,
            data_od=blok.data_od,
            data_do=koniec_zeszlego_roku
        )

        blok.tresc = nowa_tresc
        blok.data_od = poczatek_tego_roku
        blok.data_do = INFINITY_DATE
        blok.utworzone_przez_uzytkownika = request.user.username
        blok.save()

        podbloki = Podblok.objects.filter(id_bloku=blok)
        for podblok in podbloki:
            podblok_archiwalny = Podblok.objects.create(
                id_bloku=blok_archiwalny,
                kod=podblok.kod,
                tresc=podblok.tresc,
                utworzone_przez_uzytkownika=podblok.utworzone_przez_uzytkownika,
                data_od=podblok.data_od,
                data_do=koniec_zeszlego_roku
            )

            podblok.data_od = poczatek_tego_roku
            podblok.data_do = INFINITY_DATE
            podblok.utworzone_przez_uzytkownika = request.user.username
            podblok.save()

            pytania = Pytanie.objects.filter(id_podbloku=podblok)
            for pytanie in pytania:
                pytanie_archiwalne = Pytanie.objects.create(
                    id_podbloku=podblok_archiwalny,
                    kod=pytanie.kod,
                    tresc=pytanie.tresc,
                    utworzone_przez_uzytkownika=pytanie.utworzone_przez_uzytkownika,
                    data_od=pytanie.data_od,
                    data_do=koniec_zeszlego_roku
                )

                pytanie.data_od = poczatek_tego_roku
                pytanie.data_do = INFINITY_DATE
                pytanie.utworzone_przez_uzytkownika = request.user.username
                pytanie.save()

                podzapytania = Podzapytanie.objects.filter(id_pytania=pytanie)
                for podzap in podzapytania:
                    Podzapytanie.objects.create(
                        id_pytania=pytanie_archiwalne,
                        kod=podzap.kod,
                        tresc=podzap.tresc,
                        utworzone_przez_uzytkownika=podzap.utworzone_przez_uzytkownika,
                        data_od=podzap.data_od,
                        data_do=koniec_zeszlego_roku
                    )

                    podzap.data_od = poczatek_tego_roku
                    podzap.data_do = INFINITY_DATE
                    podzap.utworzone_przez_uzytkownika = request.user.username
                    podzap.save()

    def handle_edit_blok(self, request):
        blok_id = request.POST.get('blok_id')
        nowa_tresc = request.POST.get('tresc')

        if blok_id and nowa_tresc:
            blok = get_object_or_404(Blok, id=blok_id)

            if blok.czy_z_biezacego_roku(request.session['wybrany_okres']):
                blok.tresc = nowa_tresc
                blok.save()

            else:
                self.archiwe_components(request, blok, nowa_tresc)

    def get(self, request, *args, **kwargs):
        return self.list_bloki(request)

    def post(self, request, *args, **kwargs):

        if not request.session['czy_tryb_edycji']:
            return redirect(self.success_url)

        if 'add_blok' in request.POST:
            self.handle_add_blok(request)

        if 'edit_blok' in request.POST:
            self.handle_edit_blok(request)

        if 'delete_blok' in request.POST:
            self.handle_delete_blok(request)

        return redirect(self.success_url)
