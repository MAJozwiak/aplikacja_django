from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from datetime import date
from fossa2.components.pytanie.pytanie_form import PytanieForm
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.config import INFINITY_DATE
from fossa2.components.podzapytanie.podzapytanie_model import Podzapytanie
from fossa2.components.pytanie.pytanie_model import Pytanie
from fossa2.config import PYTANIE_TEMPLATE

class PytanieListView(View):
    template_name = PYTANIE_TEMPLATE

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
        id_podbloku = request.GET.get('id_podbloku', '')
        kod = request.GET.get('kod', '')
        tresc = request.GET.get('tresc', '')

        results_per_page = int(request.GET.get('results_per_page', 25))
        poczatek_roku, koniec_roku = self.load_okres_context(request)

        queryset = Pytanie.objects.filter(
                data_od__lte=koniec_roku,
                data_do__gte=poczatek_roku
            ).select_related('id_podbloku__id_bloku__id_obszaru')

        if id_obszaru: queryset = queryset.filter(id_podbloku__id_bloku__id_obszaru__kod__icontains=id_obszaru)
        if id_bloku: queryset = queryset.filter(id_podbloku__id_bloku__kod__icontains=id_bloku)
        if id_podbloku: queryset = queryset.filter(id_podbloku__kod__icontains=id_podbloku)
        if kod: queryset = queryset.filter(kod__icontains=kod)
        if tresc: queryset = queryset.filter(tresc__icontains=tresc)

        paginator = Paginator(queryset, results_per_page)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'form': PytanieForm(),
            'id_obszaru_filter': id_obszaru,
            'id_bloku_filter': id_bloku,
            'id_podbloku_filter': id_podbloku,
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

    def list_pytania(self, request, extra_context=None):
        okresy_wszystkie = self.load_okresy()

        if okresy_wszystkie.exists():
            return self.okresy_exists(request, okresy_wszystkie)
        else:
            return self.okresy_not_exists(request)



    def generate_next_code(self, podblok_rodzic):
        prefix = podblok_rodzic.kod
        ostatnie = podblok_rodzic.pytania.filter(data_do=INFINITY_DATE)

        if ostatnie.exists():
            suffixes = []
            for p in ostatnie:
                try:
                    suffix = p.kod.split('.')[-1]
                    suffixes.append(int(suffix))
                except (ValueError, IndexError):
                    continue
            next_num = max(suffixes) + 1 if suffixes else 1
            return f"{prefix}.{next_num}"
        return f"{prefix}.1"

    def handle_add_pytanie(self, request):
        form = PytanieForm(request.POST)
        if form.is_valid():
            pytanie = form.save(commit=False)
            pytanie.kod = self.generate_next_code(pytanie.id_podbloku)
            pytanie.utworzone_przez_uzytkownika = request.user.username
            pytanie.data_od = date(request.session['wybrany_okres'], 1, 1)
            pytanie.data_do = INFINITY_DATE
            pytanie.save()
        else:
            print("dodac")


    def handle_delete_pytanie(self, request):
        pyt_id = request.POST.get('pytanie_id')
        if pyt_id:
            pytanie = get_object_or_404(Pytanie, id=pyt_id)
            if pytanie.czy_z_biezacego_roku(request.session['wybrany_okres']):
                pytanie.delete()

    def archive_components(self, request, nowa_tresc, pytanie):
        koniec_zeszlego_roku = date(request.session['wybrany_okres'] - 1, 12, 31)
        poczatek_tego_roku = date(request.session['wybrany_okres'], 1, 1)


        pytanie_archiwalne = Pytanie.objects.create(
            id_podbloku=pytanie.id_podbloku,
            kod=pytanie.kod,
            tresc=pytanie.tresc,
            utworzone_przez_uzytkownika=pytanie.utworzone_przez_uzytkownika,
            data_od=pytanie.data_od,
            data_do=koniec_zeszlego_roku
        )

        pytanie.tresc = nowa_tresc
        pytanie.data_od = date(request.session['wybrany_okres'], 1, 1)
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

    def handle_edit_pytanie(self, request):
        pyt_id = request.POST.get('pytanie_id')
        nowa_tresc = request.POST.get('tresc')
        if pyt_id and nowa_tresc:
            pytanie = get_object_or_404(Pytanie, id=pyt_id)
            if pytanie.czy_z_biezacego_roku(request.session['wybrany_okres']):
                pytanie.tresc = nowa_tresc
                pytanie.save()
            else:
                self.archive_components(request, nowa_tresc, pytanie)


    def get(self, request, *args, **kwargs):
        return self.list_pytania(request)

    def post(self, request, *args, **kwargs):

        if not request.session['czy_tryb_edycji']:
            return redirect(self.success_url)

        if 'add_pytanie' in request.POST:
            self.handle_add_pytanie(request)


        if 'delete_pytanie' in request.POST:
            self.handle_delete_pytanie(request)


        if 'edit_pytanie' in request.POST:
            self.handle_edit_pytanie(request)

        return redirect(self.success_url)