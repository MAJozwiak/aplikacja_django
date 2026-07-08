from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from datetime import date
from fossa2.components.grupa.grupa_model import GrupaNaglowek
from fossa2.components.ankieta.ankieta_model import AnkietaNaglowek
from fossa2.components.ankieta.ankieta_form import AnkietaNaglowekForm
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.components.obszar.obszar_model import Obszar
from fossa2.config import INFINITY_DATE, ANKIETA_TEMPLATE

class AnkietaNaglowekListView(View):
    template_name = ANKIETA_TEMPLATE
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

        request.session['czy_tryb_edycji'] = bool(wybrany_okres and not wybrany_okres.czy_zamrozony)
        request.session['wybrany_okres'] = wybrany_okres.rok

        poczatek_roku = date(request.session['wybrany_okres'], 1, 1)
        koniec_roku = date(request.session['wybrany_okres'], 12, 31)

        return poczatek_roku, koniec_roku

    def okresy_exists(self, request, okresy_wszystkie):
        nazwa_filter = request.GET.get('nazwa', '')
        grupa_filter = request.GET.get('grupa', '')
        obszar_filter = request.GET.get('obszar', '')
        results_per_page = int(request.GET.get('results_per_page', 25))

        poczatek_roku, koniec_roku = self.load_okres_context(request)

        queryset = AnkietaNaglowek.objects.filter(
            data_od__lte=koniec_roku,
            data_do__gte=poczatek_roku
        )

        if nazwa_filter:
            queryset = queryset.filter(nazwa__icontains=nazwa_filter)
        if grupa_filter:
            queryset = queryset.filter(id_grupa__id=grupa_filter)
        if obszar_filter:
            queryset = queryset.filter(id_obszar__id=obszar_filter)

        grupy_aktywne_w_roku = GrupaNaglowek.objects.filter(
            data_od__lte=koniec_roku,
            data_do__gte=poczatek_roku
        )
        wszystkie_obszary = Obszar.objects.all()

        form = AnkietaNaglowekForm()
        form.fields['id_grupa'].queryset = grupy_aktywne_w_roku

        paginator = Paginator(queryset, results_per_page)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'form': form,
            'grupy': grupy_aktywne_w_roku,
            'obszary': wszystkie_obszary,
            'nazwa_filter': nazwa_filter,
            'grupa_filter': grupa_filter,
            'obszar_filter': obszar_filter,
            'results_per_page': results_per_page,
            'okresy_wszystkie': okresy_wszystkie,
            'wybrany_okres': request.session.get('wybrany_okres'),
            'czy_tryb_edycji': request.session.get('czy_tryb_edycji'),
        }
        return render(request, self.template_name, context)

    def okresy_not_exists(self, request):
        return render(request, self.template_name, {'brak_danych': True})

    def list_ankiety(self, request):
        okresy_wszystkie = self.load_okresy()
        if okresy_wszystkie.exists():
            return self.okresy_exists(request, okresy_wszystkie)
        else:
            return self.okresy_not_exists(request)

    def handle_add_ankieta(self, request):
        rok = request.session.get('wybrany_okres')
        poczatek = date(rok, 1, 1)
        koniec = date(rok, 12, 31)

        form = AnkietaNaglowekForm(request.POST)
        form.fields['id_grupa'].queryset = GrupaNaglowek.objects.filter(
            data_od__lte=koniec,
            data_do__gte=poczatek
        )

        if form.is_valid():
            ankieta = form.save(commit=False)
            ankieta.utworzone_przez_uzytkownika = request.user.username
            ankieta.data_od = poczatek
            ankieta.data_do = INFINITY_DATE
            obszar_obj = ankieta.id_obszar
            if obszar_obj:
                ankieta.kod_obszaru_snapshot = obszar_obj.kod

            ankieta.save()
        else:
            pass

    def handle_delete_ankieta(self, request):
        ankieta_id = request.POST.get('ankieta_id')
        rok = request.session.get('wybrany_okres')
        poczatek_roku = date(rok, 1, 1)

        ankieta = get_object_or_404(AnkietaNaglowek, id=ankieta_id)

        if ankieta.data_od >= poczatek_roku:
            ankieta.delete()
        else:
            ankieta.data_do = date(rok - 1, 12, 31)
            ankieta.save()

    def get(self, request, *args, **kwargs):
        return self.list_ankiety(request)

    def post(self, request, *args, **kwargs):
        self.load_okres_context(request)

        if not request.session.get('czy_tryb_edycji'):
            return HttpResponseForbidden("Okres jest zamrożony.")

        if 'add_ankieta' in request.POST:
            self.handle_add_ankieta(request)

        if 'delete_ankieta' in request.POST:
            self.handle_delete_ankieta(request)

        return redirect(self.success_url)