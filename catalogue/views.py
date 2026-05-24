from django.shortcuts import render
from .models import CatalogueModule


def catalogue_list(request):
    modules = CatalogueModule.objects.filter(est_actif=True)
    return render(request, 'catalogue/liste.html', {'modules': modules})
