from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from fossa2.components.podblok.podblok_form import PodblokForm
from datetime import date
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.config import INFINITY_DATE, PODBLOK_TEMPLATE
from fossa2.components.podzapytanie.podzapytanie_model import Podzapytanie
from fossa2.components.podblok.podblok_model import Podblok
from fossa2.components.pytanie.pytanie_model import Pytanie

class PodblokListView(View):
    template_name = PODBLOK_TEMPLATE

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

        request.session['czy_tryb_edycji'] = bool(wybrany_okres and not wybrany_okres.czy_zamrozony)
        request.session['wybrany_okres'] = wybrany_okres.rok

        poczatek_roku = date(request.session['wybrany_okres'], 1, 1)
        koniec_roku = date(request.session['wybrany_okres'], 12, 31)

        return poczatek_roku, koniec_roku

    def okresy_exists(self, request, okresy_wszystkie):
        id_obszaru = request.GET.get('id_obszaru', '')
        id_bloku = request.GET.get('id_bloku', '')
        kod = request.GET.get('kod', '')
        tresc = request.GET.get('tresc', '')

        results_per_page = int(request.GET.get('results_per_page', 25))

        poczatek_roku, koniec_roku = self.load_okres_context(request)

        queryset = Podblok.objects.filter(
            data_od__lte=koniec_roku,
            data_do__gte=poczatek_roku
        ).select_related('id_bloku__id_obszaru')

        if id_obszaru:
            queryset = queryset.filter(id_bloku__id_obszaru__kod__icontains=id_obszaru)
        if id_bloku:
            queryset = queryset.filter(id_bloku__kod__icontains=id_bloku)
        if kod:
            queryset = queryset.filter(kod__icontains=kod)
        if tresc:
            queryset = queryset.filter(tresc__icontains=tresc)

        paginator = Paginator(queryset, results_per_page)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'form': PodblokForm(),
            'id_obszaru_filter': id_obszaru,
            'id_bloku_filter': id_bloku,
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

    def list_podbloki(self, request):
        okresy_wszystkie = self.load_okresy()

        if okresy_wszystkie.exists():
            return self.okresy_exists(request, okresy_wszystkie)
        else:
            return self.okresy_not_exists(request)

    def generate_next_code(self, blok_rodzic):
        prefix = blok_rodzic.kod

        ostatnie = blok_rodzic.podbloki.filter(data_do=INFINITY_DATE)

        if ostatnie.exists():
            kody_numeryczne = []
            for pb in ostatnie:
                try:
                    suffix = pb.kod.split('.')[-1]
                    kody_numeryczne.append(int(suffix))
                except (ValueError, IndexError):
                    continue

            nastepny_numer = max(kody_numeryczne) + 1 if kody_numeryczne else 1
            return f"{prefix}.{nastepny_numer}"

        return f"{prefix}.1"

    def handle_add_podblok(self, request):
        form = PodblokForm(request.POST)
        if form.is_valid():
            podblok = form.save(commit=False)
            podblok.kod = self.generate_next_code(podblok.id_bloku)
            podblok.utworzone_przez_uzytkownika = request.user.username
            podblok.data_od = date(request.session['wybrany_okres'], 1, 1)
            podblok.data_do = INFINITY_DATE
            podblok.save()
        else:
            print("Dodać message")

    def handle_delete_podblok(self, request):
        podblok_id = request.POST.get('podblok_id')
        if podblok_id:
            podblok = get_object_or_404(Podblok, id=podblok_id)

            if podblok.czy_z_biezacego_roku(request.session['wybrany_okres']):
                podblok.delete()


    def archive_components(self, request, nowa_tresc, podblok):
        koniec_zeszlego_roku = date(request.session['wybrany_okres'] - 1, 12, 31)
        poczatek_tego_roku = date(request.session['wybrany_okres'], 1, 1)

        podblok_archiwalny = Podblok.objects.create(
            id_bloku=podblok.id_bloku,
            kod=podblok.kod,
            tresc=podblok.tresc,
            utworzone_przez_uzytkownika=podblok.utworzone_przez_uzytkownika,
            data_od=podblok.data_od,
            data_do=koniec_zeszlego_roku
        )

        podblok.tresc = nowa_tresc
        podblok.data_od = date(request.session['wybrany_okres'], 1, 1)
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

    def handle_edit_podblok(self, request):
        podblok_id = request.POST.get('podblok_id')
        nowa_tresc = request.POST.get('tresc')

        if podblok_id and nowa_tresc:
            podblok = get_object_or_404(Podblok, id=podblok_id)

            if podblok.czy_z_biezacego_roku(request.session['wybrany_okres']):
                podblok.tresc = nowa_tresc
                podblok.save()
            else:
                self.archive_components(request, nowa_tresc, podblok)

    def get(self, request, *args, **kwargs):
        return self.list_podbloki(request)

    def post(self, request, *args, **kwargs):

        if not request.session['czy_tryb_edycji']:
            return redirect(self.success_url)

        if 'add_podblok' in request.POST:
            self.handle_add_podblok(request)

        if 'edit_podblok' in request.POST:
            self.handle_edit_podblok(request)

        if 'delete_podblok' in request.POST:
            self.handle_delete_podblok(request)

        return redirect(self.success_url)
