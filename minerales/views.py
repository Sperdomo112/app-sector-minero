from datetime import datetime
from django.shortcuts import render
import requests
from .models import PrecioMineral  # Tu modelo real


def lista_precios_view(request):
    # ========================================================
    # 1. ACTUALIZACIÓN AUTOMÁTICA MEDIANTE API (datos.gov.co)
    # ========================================================
    try:
        # Endpoint de la API (aquí va la URL real del set de datos que uses)
        url_api = "https://datos.gov.co/resource/ejemplo-minerales.json"
        respuesta = requests.get(url_api, timeout=5)

        if respuesta.status_code == 200:
            datos_api = respuesta.json()

            for registro in datos_api:
                # Mapeamos los campos que vienen de la API con los de tu modelo PrecioMineral
                nombre = registro.get("nombre_mineral")
                precio_api = float(registro.get("precio"))
                fecha_str = registro.get("fecha")  # Ej: "2026-05-29"
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()

                # update_or_create busca si ya existe ese registro por fecha y nombre.
                # Si existe, lo actualiza con el precio de la API; si no, lo crea.
                PrecioMineral.objects.update_or_create(
                    nombre=nombre,
                    fecha=fecha_obj,
                    defaults={
                        "precio": precio_api,
                        "unidad_medida": registro.get("unidad", "Kilogramo"),
                    },
                )
    except Exception as e:
        # Si no hay internet o falla la API, la app no se cae, usa lo que ya tiene
        print(f"Error al conectar con la API: {e}")

    # ========================================================
    # 2. CONSULTA DE DATOS EN LA BASE DE DATOS LOCAL
    # ========================================================
    # Conservamos tu consulta original intacta ordenada por fecha más reciente
    precios = PrecioMineral.objects.all().order_by("-fecha", "nombre")

    # ========================================================
    # 3. RETORNO DEL CONTEXTO HACIA LA PLANTILLA HTML
    # ========================================================
    return render(
        request,
        "lista_precios.html",
        {
            "precios": precios,
        },
    )