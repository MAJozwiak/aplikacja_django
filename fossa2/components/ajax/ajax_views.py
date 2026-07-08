from fossa2.components.pytanie.pytanie_model import Pytanie
from fossa2.components.blok.blok_model import Blok
from fossa2.components.podblok.podblok_model import Podblok
from django.http import JsonResponse
from fossa2.config import INFINITY_DATE

def ajax_load_bloki(request):
    obszar_id = request.GET.get('id_obszaru')
    bloki = Blok.objects.filter(id_obszaru_id=obszar_id,data_do=INFINITY_DATE)
    print(Blok.objects)
    print(bloki)
    data = [{'id': b.id, 'kod': b.kod, 'tresc': b.tresc[:30]} for b in bloki]
    return JsonResponse(data, safe=False)

def ajax_load_podbloki(request):
    print("xxxxxxxxxx")
    blok_id = request.GET.get('id_bloku')
    podbloki = Podblok.objects.filter(id_bloku_id=blok_id,data_do=INFINITY_DATE).order_by('kod')
    print(podbloki)
    data = [{'id': p.id, 'kod': p.kod, 'tresc': p.tresc[:30]} for p in podbloki]
    return JsonResponse(data, safe=False)


def ajax_load_pytania(request):
    podblok_id = request.GET.get('id_podbloku')
    pytania = Pytanie.objects.filter(id_podbloku_id=podblok_id,data_do=INFINITY_DATE).order_by('kod')

    data = [
        {
            'id': py.id,
            'kod': py.kod,
            'tresc': py.tresc[:40] + '...' if len(py.tresc) > 40 else py.tresc
        }
        for py in pytania
    ]
    return JsonResponse(data, safe=False)
