from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from datetime import date
from .grupa_podmiotow_model import GrupaPodmioty
from .grupa_podmiotow_form import GrupaPodmiotyForm
from fossa2.components.grupa.grupa_model import GrupaNaglowek
from fossa2.components.podmiot.podmiot_model import Podmiot
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from django.http import HttpResponseForbidden
from fossa2.config import GRUPA_PODMIOTOW_TEMPLATE, INFINITY_DATE



class GrupaPodmiotyListView(View):
    template_name = GRUPA_PODMIOTOW_TEMPLATE
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
        grupa_filter = request.GET.get('grupa', '')
        podmiot_filter = request.GET.get('podmiot', '')
        results_per_page = int(request.GET.get('results_per_page', 25))

        poczatek_roku, koniec_roku = self.load_okres_context(request)

        queryset = GrupaPodmioty.objects.filter(
            data_od__lte=koniec_roku,
            data_do__gte=poczatek_roku
        ).select_related('id_grupa', 'id_podmiotu')

        if grupa_filter:
            queryset = queryset.filter(id_grupa__nazwa__icontains=grupa_filter)
        if podmiot_filter:
            queryset = queryset.filter(id_podmiotu__nazwa__icontains=podmiot_filter)

        grupy_aktywne_w_roku = GrupaNaglowek.objects.filter(
            data_od__lte=koniec_roku,
            data_do__gte=poczatek_roku
        )
        wszystkie_podmioty = Podmiot.objects.all()

        form = GrupaPodmiotyForm()
        form.fields['id_grupa'].queryset = grupy_aktywne_w_roku

        paginator = Paginator(queryset, results_per_page)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'form': form,
            'grupy': grupy_aktywne_w_roku,
            'podmioty': wszystkie_podmioty,
            'grupa_filter': grupa_filter,
            'podmiot_filter': podmiot_filter,
            'results_per_page': results_per_page,
            'okresy_wszystkie': okresy_wszystkie,
            'wybrany_okres': request.session.get('wybrany_okres'),
            'czy_tryb_edycji': request.session.get('czy_tryb_edycji'),
        }
        return render(request, self.template_name, context)

    def okresy_not_exists(self, request):
        return render(request, self.template_name, {'brak_danych': True})

    def list_grupa_podmioty(self, request):
        okresy_wszystkie = self.load_okresy()
        if okresy_wszystkie.exists():
            return self.okresy_exists(request, okresy_wszystkie)
        else:
            return self.okresy_not_exists(request)

    def handle_add_grupa_podmioty(self, request):
        rok = request.session.get('wybrany_okres')
        poczatek = date(rok, 1, 1)
        koniec = date(rok, 12, 31)

        form = GrupaPodmiotyForm(request.POST)
        form.fields['id_grupa'].queryset = GrupaNaglowek.objects.filter(
            data_od__lte=koniec,
            data_do__gte=poczatek
        )

        if form.is_valid():
            grupa = form.cleaned_data['id_grupa']
            selected_podmioty = request.POST.getlist('selected_podmioty')

            for podmiot_id in selected_podmioty:
                if podmiot_id:
                    podmiot_obj = get_object_or_404(Podmiot, id=podmiot_id)
                    if not GrupaPodmioty.objects.filter(id_grupa=grupa, id_podmiotu=podmiot_obj, data_od=poczatek).exists():
                        GrupaPodmioty.objects.create(
                            id_grupa=grupa,
                            id_podmiotu=podmiot_obj,
                            utworzone_przez_uzytkownika=request.user.username,
                            data_od=poczatek,
                            data_do=INFINITY_DATE,
                            nazwa_podmiotu_snapshot=podmiot_obj.nazwa[:10]
                        )

    def handle_delete_grupa_podmioty(self, request):
        gp_id = request.POST.get('grupa_podmioty_id')
        rok = request.session.get('wybrany_okres')
        poczatek_roku = date(rok, 1, 1)

        relacja = get_object_or_404(GrupaPodmioty, id=gp_id)

        if relacja.data_od >= poczatek_roku:
            relacja.delete()
        else:
            relacja.data_do = date(rok - 1, 12, 31)
            relacja.save()

    def get(self, request, *args, **kwargs):
        return self.list_grupa_podmioty(request)

    def post(self, request, *args, **kwargs):
        self.load_okres_context(request)

        if not request.session.get('czy_tryb_edycji'):
            return HttpResponseForbidden("Okres jest zamrożony.")

        if 'add_grupa_podmioty' in request.POST:
            self.handle_add_grupa_podmioty(request)

        if 'delete_grupa_podmioty' in request.POST:
            self.handle_delete_grupa_podmioty(request)

        return redirect(self.success_url)