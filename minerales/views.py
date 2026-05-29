from datetime import datetime
from django.shortcuts import render
import requests
from .models import PrecioMineral


def lista_precios_view(request):
    # ========================================================
    # 1. ACTUALIZACIÓN REAL DESDE DATOS.GOV.CO
    # ========================================================
    try:
        # Endpoint REAL de la Agencia Nacional de Minería (ANM)
        url_api = "https://www.datos.gov.co/api/v3/views/9gcr-rggw/query.json"
        respuesta = requests.get(url_api, timeout=5)

        if respuesta.status_code == 200:
            datos_api = respuesta.json()

            for registro in datos_api:
                # Nombres exactos de las columnas en la API oficial:
                nombre = registro.get("mineral")
                precio_raw = registro.get("precio_del_dia")
                fecha_str = registro.get(
                    "fecha"
                )  # La API devuelve texto tipo "2026-05-29T00:00:00.000"

                # Validar que existan los datos esenciales en la fila
                if nombre and precio_raw and fecha_str:
                    # Limpiamos la fecha de la API para dejar solo "YYYY-MM-DD"
                    fecha_limpia = fecha_str.split("T")[0]
                    fecha_obj = datetime.strptime(fecha_limpia, "%Y-%m-%d").date()

                    # Convertir el precio a número decimal
                    precio_api = float(precio_raw)

                    # Guardar o actualizar en tu SQLite local
                    PrecioMineral.objects.update_or_create(
                        nombre=nombre,
                        fecha=fecha_obj,
                        defaults={
                            "precio": precio_api,
                            "unidad_medida": registro.get(
                                "unidad_de_medida", "Kilogramo"
                            ),
                        },
                    )
    except Exception as e:
        # Esto te mostrará en la terminal si algo sale mal con el formato
        print(f"Error real en la API: {e}")

    # ========================================================
    # 2. CONSULTA Y RENDERIZADO
    # ========================================================
    precios = PrecioMineral.objects.all().order_by("-fecha", "nombre")

    return render(
        request,
        "lista_precios.html",
        {
            "precios": precios,
        },
    )