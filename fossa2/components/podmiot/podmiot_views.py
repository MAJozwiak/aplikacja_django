from datetime import date
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from fossa2.config import INFINITY_DATE
from fossa2.components.podmiot.podmiot_form import PodmiotForm
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.config import PODMIOT_TEMPLATE
from .podmiot_model import Podmiot
from ..grupa_podmiotow.grupa_podmiotow_model import GrupaPodmioty


class PodmiotListView(View):
    template_name = PODMIOT_TEMPLATE

    def add_podmiot(self, request):
        form = PodmiotForm(request.POST)
        if form.is_valid():
            podmiot = form.save(commit=False)
            podmiot.utworzone_przez_uzytkownika = request.user.username
            podmiot.save()
        else:
            print("kod istnieje w bazie")
            # dodać implemetnacje informacje na stronie ze kod istnieje juz w bazie

    def delete_podmiot(self, request):
        podmiot_id = request.POST.get('podmiot_id')
        podmiot = get_object_or_404(Podmiot, id=podmiot_id)
        aktywny_okres = OkresSprawozdawczy.get_aktywny_rok()
        aktywny_rok_int = aktywny_okres.rok

        relacje_grupy = GrupaPodmioty.objects.filter(
            id_podmiotu=podmiot,
            data_do=INFINITY_DATE
        )

        for relacja in relacje_grupy:
            relacja.data_do = date(aktywny_rok_int, 12, 31)
            relacja.save()
        podmiot.delete()

    def list_podmiot(self, request):
        kod_filter = request.GET.get('kod', '')
        nazwa_filter = request.GET.get('nazwa', '')

        podmioty = Podmiot.objects.all()

        if kod_filter:
            podmioty = podmioty.filter(kod__icontains=kod_filter)
        if nazwa_filter:
            podmioty = podmioty.filter(nazwa__icontains=nazwa_filter)

        results_per_page = int(request.GET.get('results_per_page', 25))

        paginator = Paginator(podmioty, results_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'kod_filter': kod_filter,
            'nazwa_filter': nazwa_filter,
            'results_per_page': results_per_page,
            'form': PodmiotForm()
        }

        return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        return self.list_podmiot(request)

    def post(self, request, *args, **kwargs):
        success_url = request.META.get('HTTP_REFERER', request.path_info)

        if 'add_podmiot' in request.POST:
            self.add_podmiot(request)

        elif 'delete_podmiot' in request.POST:
            self.delete_podmiot(request)

        return redirect(success_url)
