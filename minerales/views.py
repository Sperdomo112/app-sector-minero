import base64
from datetime import datetime
from io import BytesIO
import matplotlib

# Configuración obligatoria para que Matplotlib funcione en Render sin entorno gráfico
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from django.shortcuts import render
import requests
from .models import PrecioMineral


def lista_precios_view(request):
    # ========================================================
    # 1. CONSUMO DE API Y ACTUALIZACIÓN EN SCONCE (BASE DE DATOS)
    # ========================================================
    try:
        # Endpoint Socrata v3 de Datos Abiertos Colombia sugerido por Santiago
        url_api = "https://www.datos.gov.co/api/v3/views/9gcr-rggw/query.json"
        respuesta = requests.get(url_api, timeout=5)

        if respuesta.status_code == 200:
            datos_api = respuesta.json()

            # Estructura Socrata v3 agrupa las filas dentro del nodo 'results'
            registros = datos_api.get("results", [])

            for fila in registros:
                registro = fila.get("value", fila)

                # Mapeo tolerante a variaciones de columnas del gobierno
                nombre = registro.get("mineral") or registro.get("producto")
                precio_raw = registro.get("precio") or registro.get(
                    "precio_del_dia"
                )
                fecha_str = registro.get("fecha") or registro.get(
                    "fecha_de_cotizacion"
                )

                if nombre and precio_raw and fecha_str:
                    # Formateo seguro de fecha omitiendo la estampa de tiempo 'T00:00:00'
                    fecha_limpia = str(fecha_str).split("T")[0]
                    fecha_obj = datetime.strptime(fecha_limpia, "%Y-%m-%d").date()

                    # Conversión limpia a flotante
                    precio_api = float(precio_raw)

                    # Guardado inteligente: actualiza si existe, crea si no (evita duplicados)
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
            print(
                f"--- Error en API. Código de respuesta: {respuesta.status_code} ---"
            )

    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN EL PROCESAMIENTO: {str(e)}")

    # ========================================================
    # 2. PROCESAMIENTO ESTADÍSTICO (MATPLOTLIB A BASE64)
    # ========================================================
    # Traemos el histórico en orden cronológico ascendente para armar las curvas bien
    precios_historicos = PrecioMineral.objects.all().order_by("fecha")

    # Agrupamos los puntos por cada tipo de mineral detectado
    datos_graficas = {}
    for p in precios_historicos:
        if p.nombre not in datos_graficas:
            datos_graficas[p.nombre] = {"fechas": [], "precios": []}
        datos_graficas[p.nombre]["fechas"].append(p.fecha)
        datos_graficas[p.nombre]["precios"].append(p.precio)

    # Diccionario contenedor para pasar las imágenes al HTML
    graficas_base64 = {}

    for mineral, datos in datos_graficas.items():
        # Validamos que existan mínimo dos puntos para trazar una recta/curva
        if len(datos["fechas"]) >= 2:
            plt.figure(figsize=(6, 3))

            # Renderizado de línea estilizada
            plt.plot(
                datos["fechas"],
                datos["precios"],
                marker="o",
                linestyle="-",
                color="#2563eb",
                linewidth=2,
            )

            # Ajustes visuales rápidos del gráfico
            plt.title(f"Evolución - {mineral}", fontsize=10, fontweight="bold")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.xticks(rotation=25, fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()

            # Guardado lógico en buffer de bytes para no saturar almacenamiento físico
            buffer = BytesIO()
            plt.savefig(buffer, format="png", dpi=140)
            buffer.seek(0)
            imagen_bytes = buffer.getvalue()
            buffer.close()
            plt.close()  # Gestión de memoria del sistema

            # Codificación a cadena legible por etiquetas de imagen HTML
            grafica_b64 = base64.b64encode(imagen_bytes).decode("utf-8")
            graficas_base64[mineral] = grafica_b64

    # ========================================================
    # 3. CONSTRUCCIÓN DE LA TABLA CLÁSICA (ORDEN DESCENDENTE)
    # ========================================================
    precios_tabla = PrecioMineral.objects.all().order_by("-fecha", "nombre")

    return render(
        request,
        "lista_precios.html",
        {
            "precios": precios_tabla,
            "graficas": graficas_base64,
        },
    )