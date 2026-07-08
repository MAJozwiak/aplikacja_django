from datetime import date
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from .obszar_form import ObszarForm
from fossa2.components.ankieta.ankieta_model import AnkietaNaglowek
from fossa2.components.obszar.obszar_model import Obszar
from fossa2.config import OBSZAR_TEMPLATE, INFINITY_DATE

class ObszarListView(View):
    template_name = OBSZAR_TEMPLATE

    def add_obszar(self, request):
        form = ObszarForm(request.POST)
        if form.is_valid():
            obszar = form.save(commit=False)
            obszar.utworzone_przez_uzytkownika = request.user.username
            obszar.save()
        else:
            print("dodac obslugje messege dla tej samej nazwy / kod -> ze blad")

    def delete_obszar(self, request):
        obszar_id = request.POST.get('obszar_id')
        obszar = get_object_or_404(Obszar, id=obszar_id)
        aktywny_okres = OkresSprawozdawczy.get_aktywny_rok()
        aktywny_rok_int = aktywny_okres.rok
        ankiety = AnkietaNaglowek.objects.filter(
            id_obszar=obszar,
            data_do=INFINITY_DATE
        )

        for ankieta in ankiety:
            ankieta.data_do = date(aktywny_rok_int, 12, 31)
            ankieta.save()
        obszar.delete()

    def list_obszar(self, request):
        kod_filter = request.GET.get('kod', '')
        nazwa_filter = request.GET.get('nazwa', '')
        results_per_page = int(request.GET.get('results_per_page', 25))

        obszary = Obszar.objects.all()

        if kod_filter:
            obszary = obszary.filter(kod__icontains=kod_filter)
        if nazwa_filter:
            obszary = obszary.filter(nazwa__icontains=nazwa_filter)

        paginator = Paginator(obszary, results_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'kod_filter': kod_filter,
            'nazwa_filter': nazwa_filter,
            'results_per_page': results_per_page,
            'form': ObszarForm(),
        }
        return render(request, self.template_name, context)

    def get(self, request):
        return self.list_obszar(request)

    def post(self, request):
        success_url = request.META.get('HTTP_REFERER', request.path_info)

        if 'add_obszar' in request.POST:
            self.add_obszar(request)

        elif 'delete_obszar' in request.POST:
            self.delete_obszar(request)

        return redirect(success_url)
