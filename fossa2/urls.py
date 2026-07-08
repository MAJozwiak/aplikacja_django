from fossa2.components.ankieta_pytania.ankieta_pytania_views import AnkietaPytaniaListView
from fossa2.components.grupa_podmiotow.grupa_podmiotow_views import GrupaPodmiotyListView
from fossa2.components.ankieta.ankieta_views import AnkietaNaglowekListView
from fossa2.components.grupa.grupa_views import GrupaNaglowekListView
from fossa2.components.ajax import ajax_views
from django.urls import path, include
from fossa2.components.podzapytanie.podzapytanie_views import PodzapytanieListView
from fossa2.components.menu.menu_views import HomeView
from fossa2.components.obszar.obszar_views import ObszarListView
from fossa2.components.podmiot.podmiot_views import PodmiotListView
from fossa2.components.blok.blok_views import BlokListView
from fossa2.components.podblok.podblok_views import PodblokListView
from fossa2.components.rejestracja.rejestracja_views import register
from fossa2.components.pytanie.pytanie_views import PytanieListView
from fossa2.components.slownik.slownik_views import manage_slownik
from fossa2.components.generowanie_formularzy.generowanie_formularzy_view import GenerowanieFormularzyView

urlpatterns = [
    path('', HomeView.as_view(), name='strona_glowna'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
    path('obszary/', ObszarListView.as_view(), name='obszar_list'),
    path('podmiot_list/', PodmiotListView.as_view(), name='podmiot_list'),
    path('bloki/', BlokListView.as_view(), name='blok_list'),
    path('podblok/', PodblokListView.as_view(), name='podblok_list'),
    path('ajax/load-bloki/', ajax_views.ajax_load_bloki, name='ajax_load_bloki'),
    path('ajax/load-podbloki/', ajax_views.ajax_load_podbloki, name='ajax_load_podbloki'),
    path('ajax/load-pytania/', ajax_views.ajax_load_pytania, name='ajax_load_pytania'),
    path('slowniki/', manage_slownik, name='slownik_list'),

    path('pytania/', PytanieListView.as_view(), name='pytanie_list'),
    path('podzapytania/', PodzapytanieListView.as_view(), name='podzapytanie_list'),
    path('grupy-naglowkow/', GrupaNaglowekListView.as_view(), name='grupanaglowek_list'),
    path('grupy-podmiotow/', GrupaPodmiotyListView.as_view(), name='grupa_podmioty_list'),
    path('ankieta-naglowek/', AnkietaNaglowekListView.as_view(), name='ankieta_naglowek_list'),
    path('ankieta-pytania/', AnkietaPytaniaListView.as_view(), name='ankieta_pytania_list'),
    path('generowanie-formularzy/', GenerowanieFormularzyView.as_view(), name='generowanie_formularzy'),
]