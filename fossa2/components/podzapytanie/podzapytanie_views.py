from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from datetime import date
from fossa2.components.slownik.slownik_model import Slownik
from fossa2.components.podzapytanie.podzapytanie_form import PodzapytanieForm
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.config import INFINITY_DATE
from fossa2.components.podzapytanie.podzapytanie_model import Podzapytanie
from fossa2.config import PODZAPYTANIE

class PodzapytanieListView(View):
    template_name = PODZAPYTANIE

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
        id_obszar = request.GET.get('id_obszaru', '')
        id_blok = request.GET.get('id_bloku', '')
        id_podbloku = request.GET.get('id_podbloku', '')
        pyt = request.GET.get('id_pytania', '')
        kod = request.GET.get('kod', '')
        tresc = request.GET.get('tresc', '')

        results_per_page = int(request.GET.get('results_per_page', 25))

        poczatek_roku, koniec_roku = self.load_okres_context(request)


        queryset = Podzapytanie.objects.filter(
                data_od__lte=koniec_roku,
                data_do__gte=poczatek_roku
            ).select_related('id_pytania__id_podbloku__id_bloku__id_obszaru')


        if id_obszar: queryset = queryset.filter(id_pytania__id_podbloku__id_bloku__id_obszaru__kod__icontains=id_obszar)
        if id_blok: queryset = queryset.filter(id_pytania__id_podbloku__id_bloku__kod__icontains=id_blok)
        if id_podbloku: queryset = queryset.filter(id_pytania__id_podbloku__kod__icontains=id_podbloku)
        if pyt: queryset = queryset.filter(id_pytania__kod__icontains=pyt)
        if kod: queryset = queryset.filter(kod__icontains=kod)
        if tresc: queryset = queryset.filter(tresc__icontains=tresc)

        paginator = Paginator(queryset, results_per_page)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'form': PodzapytanieForm(),
            'id_obszaru_filter': id_obszar,
            'id_bloku_filter': id_blok,
            'id_podbloku_filter': id_podbloku,
            'id_pytania_filter': pyt,
            'kod_filter': kod,
            'tresc_filter': tresc,
            'results_per_page': results_per_page,
            'okresy_wszystkie': okresy_wszystkie,
            'slowniki': Slownik.objects.all(),
            'wybrany_okres': request.session['wybrany_okres'],
            'czy_tryb_edycji': request.session['czy_tryb_edycji'],
        }
        return render(request, self.template_name, context)
    def okresy_not_exists(self, request):
        return render(request, self.template_name, {'brak_danych': True})
    def list_podzapytanie(self, request):
        okresy_wszystkie = self.load_okresy()

        if okresy_wszystkie.exists():
            return self.okresy_exists(request, okresy_wszystkie)
        else:
            return self.okresy_not_exists(request)

    def generate_next_code(self, pytanie_rodzic):
        prefix = pytanie_rodzic.kod
        ostatnie = pytanie_rodzic.podzapytania.filter(data_do=INFINITY_DATE)
        if ostatnie.exists():
            suffixes = []
            for pz in ostatnie:
                try:
                    suffix = pz.kod.split('.')[-1]
                    suffixes.append(int(suffix))
                except (ValueError, IndexError):
                    continue
            next_num = max(suffixes) + 1 if suffixes else 1
            return f"{prefix}.{next_num}"
        return f"{prefix}.1"

    def handle_add_podzapytanie(self, request):
        form = PodzapytanieForm(request.POST)
        if form.is_valid():
            pz = form.save(commit=False)
            pz.kod = self.generate_next_code(pz.id_pytania)
            pz.utworzone_przez_uzytkownika = request.user.username
            pz.data_od = date(request.session['wybrany_okres'], 1, 1)
            pz.data_do = INFINITY_DATE
            if pz.slownik:
                print(f"Wybrany słownik: {pz.slownik.nazwa}")
                print(f"Opcje tego słownika: {pz.slownik.opcje}")
            pz.save()

        else:
            print("dodac message")

    def handle_delete_podzapytanie(self, request):
        pz_id = request.POST.get('podzapytanie_id')
        if pz_id:
            pz = get_object_or_404(Podzapytanie, id=pz_id)
            if pz.czy_z_biezacego_roku(request.session['wybrany_okres']):
                pz.delete()

    def handle_edit_podzapytanie(self, request):
        pz_id = request.POST.get('podzapytanie_id')
        nowa_tresc = request.POST.get('tresc')
        nowe_wytyczne = request.POST.get('wytyczne')
        czy_obligatoryjne = request.POST.get('obligatoryjne') == 'on'

        if pz_id:
            pz = get_object_or_404(Podzapytanie, id=pz_id)
            if pz.czy_z_biezacego_roku(request.session['wybrany_okres']):
                pz.tresc = nowa_tresc
                pz.wytyczne = nowe_wytyczne
                pz.obligatoryjne = czy_obligatoryjne
                pz.save()
            else:
                koniec_zeszlego_roku = date(request.session['wybrany_okres'] - 1, 12, 31)
                poczatek_tego_roku = date(request.session['wybrany_okres'], 1, 1)

                Podzapytanie.objects.create(
                    id_pytania=pz.id_pytania,
                    kod=pz.kod,
                    tresc=pz.tresc,
                    wytyczne=pz.wytyczne,
                    obligatoryjne=pz.obligatoryjne,
                    utworzone_przez_uzytkownika=pz.utworzone_przez_uzytkownika,
                    data_od=pz.data_od,
                    data_do=koniec_zeszlego_roku
                )

                pz.tresc = nowa_tresc
                pz.wytyczne = nowe_wytyczne
                pz.obligatoryjne = czy_obligatoryjne
                pz.data_od = poczatek_tego_roku
                pz.data_do = INFINITY_DATE
                pz.utworzone_przez_uzytkownika = request.user.username
                pz.save()


    def get(self, request, *args, **kwargs):
        return self.list_podzapytanie(request)

    def post(self, request, *args, **kwargs):

        if not request.session['czy_tryb_edycji']:
            return redirect(self.success_url)

        if 'add_podzapytanie' in request.POST:
            self.handle_add_podzapytanie(request)

        elif 'delete_podzapytanie' in request.POST:
            self.handle_delete_podzapytanie(request)

        elif 'edit_podzapytanie' in request.POST:
            self.handle_edit_podzapytanie(request)

        return redirect(self.success_url)