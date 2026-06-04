from django.db import models


class PrecioMineral(models.Model):
    # Opciones para restringir los tipos de minerales en el sistema
    OPCIONES_MINERAL = [
        ("ORO", "Oro"),
        ("CARBON", "Carbón"),
        ("NIQUEL", "Níquel"),
        ("COBRE", "Cobre"),
    ]

    # Opciones para las unidades de medida
    OPCIONES_UNIDAD = [
        ("GRAMO", "Gramo"),
        ("KILOGRAMO", "Kilogramo"),
    ]

    nombre = models.CharField(
        db_index=True,
        max_length=20,
        choices=OPCIONES_MINERAL,
        verbose_name="Mineral",
    )
    unidad_medida = models.CharField(
        max_length=15,
        choices=OPCIONES_UNIDAD,
        default="KILOGRAMO",
        verbose_name="Unidad de Medida",
    )
    precio_cop = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Precio (COP)"
    )
    fecha = models.DateField(verbose_name="Fecha de Cotización")
    fecha_registro = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Registro en Sistema"
    )

    class Meta:
        verbose_name = "Precio de Mineral"
        verbose_name_plural = "Historial de Precios"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.get_nombre_display()} ({self.get_unidad_medida_display()}) - ${self.precio_cop:,.2f}"