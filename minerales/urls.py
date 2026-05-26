from django.urls import path
from .views import lista_precios_view

urlpatterns = [
    # Cuando el usuario entre a la raíz de la app, llamará a la vista
    path("", lista_precios_view, name="lista_precios"),
]