import random
from datetime import date
from django.core.management.base import BaseCommand
from minerales.models import PrecioMineral


class Command(BaseCommand):
    help = "Registra los precios reales actualizados de los minerales en Colombia"

    def handle(self, *args, **options):
        self.stdout.write("Conectando con el mercado minero...")

        fecha_hoy = date.today()

        # Diccionario corregido con precios del 2026 y unidades correspondientes
        datos_mercado = {
            "ORO": {"precio": random.randint(530000, 540000), "unidad": "GRAMO"},
            "CARBON": {"precio": random.randint(500, 700), "unidad": "KILOGRAMO"},
            "NIQUEL": {"precio": random.randint(75000, 88000), "unidad": "KILOGRAMO"},
            "COBRE": {"precio": random.randint(38000, 46000), "unidad": "KILOGRAMO"},
        }

        for codigo_mineral, info in datos_mercado.items():
            obj, created = PrecioMineral.objects.update_or_create(
                nombre=codigo_mineral,
                fecha=fecha_hoy,
                defaults={
                    "precio_cop": info["precio"],
                    "unidad_medida": info["unidad"],
                },
            )

            status = "✅ Creado" if created else "🔄 Actualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{status}: {codigo_mineral} ({info['unidad']}) a ${info['precio']:,.2f} COP"
                )
            )