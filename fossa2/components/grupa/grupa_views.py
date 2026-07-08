from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from datetime import date
from fossa2.components.grupa.grupa_model import GrupaNaglowek
from fossa2.components.ankieta.ankieta_model import AnkietaNaglowek
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.components.grupa.grupa_form import GrupaNaglowekForm
from fossa2.components.grupa_podmiotow.grupa_podmiotow_model import GrupaPodmioty
from fossa2.config import GRUPA_TEMPLATE, INFINITY_DATE

class GrupaNaglowekListView(View):
    template_name = GRUPA_TEMPLATE
    success_url = None

    def dispatch(self, request, *args, **kwargs):
        self.success_url = request.META.get('HTTP_REFERER', request.path_info)
        return super().dispatch(request, *args, **kwargs)

    def load_okresy(self):
        return OkresSprawozdawczy.objects.all()

    def load_okres_context(self, request):
        rok_param = request.GET.get('rok') or request.POST.get('rok')

        if rok_param:
            wybrany_okres = get_object_or_404(OkresSprawozdawczy, rok=int(rok_param))
        else:
            wybrany_okres = OkresSprawozdawczy.get_aktywny_rok() or self.load_okresy().first()

        request.session['czy_tryb_edycji'] = bool(wybrany_okres and not wybrany_okres.czy_zamrozony)
        request.session['wybrany_okres'] = wybrany_okres.rok

        poczatek_roku = date(request.session['wybrany_okres'], 1, 1)
        koniec_roku = date(request.session['wybrany_okres'], 12, 31)

        return poczatek_roku, koniec_roku

    def okresy_exists(self, request, okresy_wszystkie):
        # Pobieranie filtrów
        nazwa_filter = request.GET.get('nazwa', '')
        results_per_page = int(request.GET.get('results_per_page', 25))

        poczatek_roku, koniec_roku = self.load_okres_context(request)

        queryset = GrupaNaglowek.objects.filter(
            data_od__lte=koniec_roku,
            data_do__gte=poczatek_roku
        )

        if nazwa_filter:
            queryset = queryset.filter(nazwa__icontains=nazwa_filter)

        paginator = Paginator(queryset, results_per_page)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'form': GrupaNaglowekForm(),
            'nazwa_filter': nazwa_filter,
            'results_per_page': results_per_page,
            'okresy_wszystkie': okresy_wszystkie,
            'wybrany_okres': request.session.get('wybrany_okres'),
            'czy_tryb_edycji': request.session.get('czy_tryb_edycji'),
        }
        return render(request, self.template_name, context)

    def okresy_not_exists(self, request):
        return render(request, self.template_name, {'brak_danych': True})

    def list_grupy(self, request):
        okresy_wszystkie = self.load_okresy()
        if okresy_wszystkie.exists():
            return self.okresy_exists(request, okresy_wszystkie)
        else:
            return self.okresy_not_exists(request)

    def handle_add_grupanaglowek(self, request):
        rok = request.session.get('wybrany_okres')
        poczatek = date(rok, 1, 1)

        form = GrupaNaglowekForm(request.POST)
        if form.is_valid():
            grupa = form.save(commit=False)
            grupa.utworzone_przez_uzytkownika = request.user.username
            grupa.data_od = poczatek
            grupa.data_do = INFINITY_DATE
            grupa.save()

    def handle_delete_grupanaglowek(self, request):
        grupa_id = request.POST.get('grupanaglowek_id')
        rok = request.session.get('wybrany_okres')
        poczatek_roku = date(rok, 1, 1)

        grupa = get_object_or_404(GrupaNaglowek, id=grupa_id)

        if grupa.data_od == poczatek_roku:
            grupa.delete()
        else:
            data_zamkniecia = date(rok - 1, 12, 31)


            grupa.data_do = data_zamkniecia
            grupa.save()

            AnkietaNaglowek.objects.filter(
                id_grupa=grupa,
                data_do=INFINITY_DATE
            ).update(data_do=data_zamkniecia)

            GrupaPodmioty.objects.filter(
                id_grupa=grupa,
                data_do=INFINITY_DATE
            ).update(data_do=data_zamkniecia)

    def get(self, request, *args, **kwargs):
        return self.list_grupy(request)

    def post(self, request, *args, **kwargs):
        self.load_okres_context(request)

        if not request.session.get('czy_tryb_edycji'):
            return HttpResponseForbidden("Okres jest zamrożony.")

        if 'add_grupanaglowek' in request.POST:
            self.handle_add_grupanaglowek(request)

        if 'delete_grupanaglowek' in request.POST:
            self.handle_delete_grupanaglowek(request)

        return redirect(self.success_url)