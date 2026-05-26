from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),  # Tu panel de administración actual
    path(
        "", include("minerales.urls")
    ),  # Conecta la página de inicio con tu app de minerales
]