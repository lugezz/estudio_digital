from django.db import models

class Feriado(models.Model):
    nombre   = models.CharField(max_length=50)
    fecha = models.DateField(unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-fecha']

class GanArt23 (models.Model):
    año = models.IntegerField()
    nombre = models.CharField(max_length=50)
    importe = models.DecimalField(decimal_places=2, max_digits=10)

class GanArt90 (models.Model):
    año = models.IntegerField()
    desde = models.DecimalField(decimal_places=2, max_digits=10)
    alicuota = models.IntegerField() #de 1 a 100
