from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from fossa2.components.slownik.slownik_form import SlownikForm
from fossa2.components.slownik.slownik_model import Slownik
from fossa2.config import SLOWNIK_TEMPLATE

def manage_slownik(request):
    form = SlownikForm()

    if request.method == 'POST':
        if 'add_dropdown' in request.POST:
            form = SlownikForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('slownik_list')

        elif 'delete_dropdown' in request.POST:
            dropdown_id = request.POST.get('dropdown_id')
            item = get_object_or_404(Slownik, id=dropdown_id)
            item.delete()
            return redirect('slownik_list')

    all_slowniki = Slownik.objects.all().order_by('-id')
    paginator = Paginator(all_slowniki, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, SLOWNIK_TEMPLATE, {
        'form': form,
        'page_obj': page_obj,
    })