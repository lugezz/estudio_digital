from django.db import models
from common.models import User
from django.utils.translation import ugettext_lazy as _

class IVA(models.Model):
    IVA_CHOICES = (('compras','Compras'),('ventas', 'Ventas'))

    tipo_iva = models.CharField(max_length=20, choices=IVA_CHOICES, default='ventas')

    periodo = models.DateField()
    neto_gravado = models.DecimalField(decimal_places=2, max_digits=10)
    neto_no_gravado = models.DecimalField(decimal_places=2, max_digits=10)
    exento = models.DecimalField(decimal_places=2, max_digits=10)
    iva = models.DecimalField(decimal_places=2, max_digits=10)
    percepcion = models.DecimalField(decimal_places=2, max_digits=10)
    total = models.DecimalField(decimal_places=2, max_digits=10)

    created_by = models.ForeignKey(
        User, related_name='factura_created_by',
        on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(_("Creado el"), auto_now_add=True)

    @property
    def total(self):
        return int(self.neto_gravado + self.neto_no_gravado + self.exento + self.iva + self.percepcion)

    def __str__(self):
        return "Tipo: {} {:%m-%Y}".format(self.tipo_iva.capitalize(),self.periodo)
