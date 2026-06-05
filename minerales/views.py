import base64
from datetime import datetime
from io import BytesIO
import matplotlib

# Configuración obligatoria para que Matplotlib funcione en Render sin entorno gráfico
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.shortcuts import render
import requests
from .models import PrecioMineral


def lista_precios_view(request):
    # ========================================================
    # 1. CONSUMO DE API Y ACTUALIZACIÓN EN BASE DE DATOS
    # ========================================================
    try:
        url_api = "https://www.datos.gov.co/api/v3/views/9gcr-rggw/query.json"
        respuesta = requests.get(url_api, timeout=5)

        if respuesta.status_code == 200:
            datos_api = respuesta.json()
            registros = datos_api.get('results', [])

            for fila in registros:
                registro = fila.get('value', fila)

                nombre = registro.get('mineral') or registro.get('producto')
                precio_raw = registro.get('precio') or registro.get('precio_del_dia')
                fecha_str = registro.get('fecha') or registro.get('fecha_de_cotizacion')

                if nombre and precio_raw and fecha_str:
                    # Limpieza y formateo de la fecha
                    fecha_limpia = str(fecha_str).split('T')[0]
                    fecha_obj = datetime.strptime(fecha_limpia, '%Y-%m-%d').date()

                    # Convertimos el precio de la API a número decimal/flotante
                    precio_api = float(precio_raw)

                    # Guardamos usando 'precio_cop' que es el nombre real de tu modelo
                    PrecioMineral.objects.update_or_create(
                        nombre=nombre,
                        fecha=fecha_obj,
                        defaults={
                            'precio_cop': precio_api,
                            'unidad_medida': registro.get('unidad_medida', 'Kilogramo')
                        }
                    )
    except Exception as e:
        print(f"❌ ERROR EN EL PROCESAMIENTO DE API: {str(e)}")

    # ========================================================
    # 2. GENERACIÓN DE GRÁFICAS (USANDO PRECIO_COP)
    # ========================================================
    precios_historicos = PrecioMineral.objects.all().order_by('fecha')

    datos_graficas = {}
    for p in precios_historicos:
        if p.nombre not in datos_graficas:
            datos_graficas[p.nombre] = {'fechas': [], 'precios': []}
        datos_graficas[p.nombre]['fechas'].append(p.fecha)
        datos_graficas[p.nombre]['precios'].append(float(p.precio_cop))

    graficas_base64 = {}

    for mineral, datos in datos_graficas.items():
        if len(datos['fechas']) >= 2:
            plt.figure(figsize=(6, 3))
            plt.plot(datos['fechas'], datos['precios'], marker='o', linestyle='-', color='#2563eb', linewidth=2)
            plt.title(f"Evolución - {mineral}", fontsize=10, fontweight='bold')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.xticks(rotation=25, fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=140)
            buffer.seek(0)
            imagen_bytes = buffer.getvalue()
            buffer.close()
            plt.close()

            grafica_b64 = base64.b64encode(imagen_bytes).decode('utf-8')
            graficas_base64[mineral] = grafica_b64

    # ========================================================
    # 3. CONSULTA PARA LA TABLA (ORDEN DESCENDENTE)
    # ========================================================
    precios_tabla = PrecioMineral.objects.all().order_by('-fecha', 'nombre')

    return render(request, 'lista_precios.html', {
        'precios': precios_tabla,
        'graficas': graficas_base64,
    })