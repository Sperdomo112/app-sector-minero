from django.shortcuts import render
from .models import PrecioMineral


def lista_precios_view(request):
    # Traemos todos los precios ordenados por la fecha más reciente
    precios = PrecioMineral.objects.all().order_by("-fecha", "nombre")

    # Enviamos los datos a la plantilla HTML que acabas de crear
    return render(request, "lista_precios.html", {"precios": precios})