from datetime import datetime
from django.shortcuts import render
import requests
from .models import PrecioMineral


def lista_precios_view(request):
    # ========================================================
    # 1. ACTUALIZACIÓN DESDE EL ENDPOINT DE SANTIAGO
    # ========================================================
    try:
        url_api = "https://www.datos.gov.co/api/v3/views/9gcr-rggw/query.json"
        respuesta = requests.get(url_api, timeout=5)

        if respuesta.status_code == 200:
            datos_api = respuesta.json()

            # El formato query.json de la v3 de Socrata mete las filas dentro de 'results'
            registros = datos_api.get("results", [])

            for fila in registros:
                # Extraemos los datos del sub-diccionario 'value' que usa la API v3
                registro = fila.get("value", fila)

                # Mapeo exacto de las columnas de la API
                nombre = registro.get("mineral") or registro.get("producto")
                precio_raw = registro.get("precio") or registro.get(
                    "precio_del_dia"
                )
                fecha_str = registro.get("fecha") or registro.get(
                    "fecha_de_cotizacion"
                )

                if nombre and precio_raw and fecha_str:
                    # Limpiar la fecha (quitarle la T de la hora si la trae)
                    fecha_limpia = str(fecha_str).split("T")[0]
                    fecha_obj = datetime.strptime(fecha_limpia, "%Y-%m-%d").date()

                    # Convertir precio a flotante de forma segura
                    precio_api = float(precio_raw)

                    # Guardar o actualizar
                    PrecioMineral.objects.update_or_create(
                        nombre=nombre,
                        fecha=fecha_obj,
                        defaults={
                            "precio": precio_api,
                            "unidad_medida": registro.get(
                                "unidad_medida", "Kilogramo"
                            ),
                        },
                    )
            print(
                f"--- Sincronización exitosa. Registros procesados: {len(registros)} ---"
            )
        else:
            print(f"--- API respondió con código de error: {respuesta.status_code} ---")

    except Exception as e:
        # ¡ESTO ES CLAVE! Si hay un error de formato, Render lo gritará en los Logs
        print(f"ERROR CRÍTICO EN EL BACKEND: {str(e)}")

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