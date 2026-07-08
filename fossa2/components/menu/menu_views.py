from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from fossa2.components.okres_sprawozdawczy.okres_sprawozdawczy_model import OkresSprawozdawczy
from fossa2.config import MENU_TEMPLATE
class HomeView(LoginRequiredMixin,View):
    template_name = MENU_TEMPLATE

    def get(self, request, *args, **kwargs):
        aktywny_rok = OkresSprawozdawczy.get_aktywny_rok()

        context = {
            'aktywny_rok': aktywny_rok,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'zamroz_rok' in request.POST:
            aktywny_rok = OkresSprawozdawczy.get_aktywny_rok()
            if aktywny_rok:
                aktywny_rok.zamroz_i_utworz_kolejny()
        return redirect(request.path_info)