import re
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from datetime import date
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.components.podzapytanie.podzapytanie_model import Podzapytanie
from .ankieta_pytania_form import AnkietaPytaniaForm
from .ankieta_pytania_model import AnkietaPytania
from fossa2.components.ankieta.ankieta_model import AnkietaNaglowek
from fossa2.config import INFINITY_DATE, ANKIETA_PYTANIA_TEMPLATE

class AnkietaPytaniaListView(View):
    template_name = ANKIETA_PYTANIA_TEMPLATE
    success_url = None

    def dispatch(self, request, *args, **kwargs):
        self.success_url = request.META.get('HTTP_REFERER', request.path_info)
        return super().dispatch(request, *args, **kwargs)

    def get_natural_sort_key(self, value):
        if not value: return []
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', str(value))]

    def get_poczatek_roku(self, request):
        rok = request.session.get('wybrany_okres')
        if not rok:
            najnowszy = OkresSprawozdawczy.objects.order_by('-rok').first()
            rok = najnowszy.rok if najnowszy else date.today().year
        return date(rok, 1, 1)

    def list_ankieta_pytania(self, request):
        poczatek_roku = self.get_poczatek_roku(request)
        koniec_roku = date(poczatek_roku.year, 12, 31) # Definicja, by uniknąć NameError

        ankieta_filter = request.GET.get('ankieta', '')
        obszar_filter = request.GET.get('obszar', '')
        blok_filter = request.GET.get('blok', '')
        podblok_filter = request.GET.get('podblok', '')
        pytanie_filter = request.GET.get('pytanie', '')
        podzapytanie_filter = request.GET.get('podzapytanie', '')
        tresc_filter = request.GET.get('tresc', '')
        chosen_ankieta_id = request.GET.get('chosen_ankieta')

        rpp = request.GET.get('results_per_page', '25')
        try: results_per_page = int(rpp)
        except ValueError: results_per_page = 25

        ankieta_pytania_qs = AnkietaPytania.objects.select_related(
            'id_podzapytania__id_pytania__id_podbloku__id_bloku__id_obszaru',
            'id_ankieta_naglowek'
        ).filter(
            id_ankieta_naglowek__data_do=INFINITY_DATE, # TYLKO NIEZAMKNIĘTE
            id_podzapytania__data_do=INFINITY_DATE
        )

        if ankieta_filter: ankieta_pytania_qs = ankieta_pytania_qs.filter(id_ankieta_naglowek__nazwa__icontains=ankieta_filter)
        if obszar_filter: ankieta_pytania_qs = ankieta_pytania_qs.filter(id_podzapytania__id_pytania__id_podbloku__id_bloku__id_obszaru__kod__icontains=obszar_filter)
        if blok_filter: ankieta_pytania_qs = ankieta_pytania_qs.filter(id_podzapytania__id_pytania__id_podbloku__id_bloku__kod__icontains=blok_filter)
        if podblok_filter: ankieta_pytania_qs = ankieta_pytania_qs.filter(id_podzapytania__id_pytania__id_podbloku__kod__icontains=podblok_filter)
        if pytanie_filter: ankieta_pytania_qs = ankieta_pytania_qs.filter(id_podzapytania__id_pytania__tresc__icontains=pytanie_filter)
        if podzapytanie_filter: ankieta_pytania_qs = ankieta_pytania_qs.filter(id_podzapytania__tresc__icontains=podzapytanie_filter)

        ankieta_pytania_list = list(ankieta_pytania_qs)
        ankieta_pytania_list.sort(key=lambda obj: self.get_natural_sort_key(obj.id_podzapytania.kod if obj.id_podzapytania else ""))
        page_obj = Paginator(ankieta_pytania_list, results_per_page).get_page(request.GET.get('page'))

        wszystkie_qs = Podzapytanie.objects.select_related('id_pytania__id_podbloku__id_bloku__id_obszaru').filter(data_do=INFINITY_DATE)

        if chosen_ankieta_id:
            try:
                chosen_ankieta = AnkietaNaglowek.objects.get(id=chosen_ankieta_id)
                if chosen_ankieta.id_obszar:
                    wszystkie_qs = wszystkie_qs.filter(id_pytania__id_podbloku__id_bloku__id_obszaru=chosen_ankieta.id_obszar)
            except AnkietaNaglowek.DoesNotExist: pass

        if obszar_filter: wszystkie_qs = wszystkie_qs.filter(id_pytania__id_podbloku__id_bloku__id_obszaru__kod__icontains=obszar_filter)
        if blok_filter: wszystkie_qs = wszystkie_qs.filter(id_pytania__id_podbloku__id_bloku__kod__icontains=blok_filter)
        if podblok_filter: wszystkie_qs = wszystkie_qs.filter(id_pytania__id_podbloku__kod__icontains=podblok_filter)
        if pytanie_filter: wszystkie_qs = wszystkie_qs.filter(id_pytania__kod__icontains=pytanie_filter)
        if podzapytanie_filter: wszystkie_qs = wszystkie_qs.filter(kod__icontains=podzapytanie_filter)
        if tresc_filter: wszystkie_qs = wszystkie_qs.filter(tresc__icontains=tresc_filter)

        wszystkie_podzapytania_list = list(wszystkie_qs)
        wszystkie_podzapytania_list.sort(key=lambda obj: self.get_natural_sort_key(obj.kod))
        wszystkie_podzapytania = Paginator(wszystkie_podzapytania_list, results_per_page).get_page(request.GET.get('page_add'))

        form = AnkietaPytaniaForm(initial={'id_ankieta_naglowek': chosen_ankieta_id})
        form.fields['id_ankieta_naglowek'].queryset = AnkietaNaglowek.objects.filter(data_do=INFINITY_DATE)

        context = {
            'page_obj': page_obj,
            'wszystkie_podzapytania': wszystkie_podzapytania,
            'form': form,
            'ankieta_filter': ankieta_filter,
            'obszar_filter': obszar_filter,
            'blok_filter': blok_filter,
            'podblok_filter': podblok_filter,
            'pytanie_filter': pytanie_filter,
            'podzapytanie_filter': podzapytanie_filter,
            'tresc_filter': tresc_filter,
            'results_per_page': results_per_page,
            'chosen_ankieta_id': chosen_ankieta_id,
        }
        return render(request, self.template_name, context)

    def handle_add(self, request):
        form = AnkietaPytaniaForm(request.POST)
        form.fields['id_ankieta_naglowek'].queryset = AnkietaNaglowek.objects.filter(data_do=INFINITY_DATE)

        if form.is_valid():
            ankieta_obj = form.cleaned_data['id_ankieta_naglowek']
            wybrane_ids = request.POST.getlist('wybrane_podzapytania')
            for pz_id in wybrane_ids:
                AnkietaPytania.objects.get_or_create(
                    id_ankieta_naglowek=ankieta_obj,
                    id_podzapytania_id=pz_id,
                    defaults={'utworzone_przez_uzytkownika': request.user.username}
                )

    def handle_delete(self, request):
        ap_id = request.POST.get('ankietapytania_id')
        get_object_or_404(AnkietaPytania, id=ap_id).delete()

    def get(self, request, *args, **kwargs):
        return self.list_ankieta_pytania(request)

    def post(self, request, *args, **kwargs):
        if 'add_ankieta_pytania' in request.POST:
            self.handle_add(request)
            return redirect('ankieta_pytania_list')
        elif 'delete_ankieta_pytania' in request.POST:
            self.handle_delete(request)
            return redirect('/ankieta-pytania/?mode=list')
        return redirect(self.success_url)