from django.contrib import admin
from .models import PrecioMineral


@admin.register(PrecioMineral)
class PrecioMineralAdmin(admin.ModelAdmin):
    # Sumamos "unidad_medida" para que se vea directo en la tabla principal
    list_display = ("nombre", "unidad_medida", "precio_cop", "fecha", "fecha_registro")

    # Filtros laterales para buscar rápido
    list_filter = ("nombre", "fecha")

    # Barra de búsqueda
    search_fields = ("nombre",)