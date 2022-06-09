from django.db import models
from django.urls import reverse
from common.models import User

class Novedad(models.Model):
    titulo   = models.CharField(max_length=120)
    contenido = models.TextField()
    activo  = models.BooleanField(default=True)
    imagen   = models.ImageField(upload_to='image/', blank=True, null=True)
    publicado= models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    asignado_a = models.ManyToManyField(User, related_name='novedad_users', blank=True)

    def get_absolute_url(self):
        return reverse("novedades:novedad-detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ['-publicado', '-actualizado', '-timestamp']

    def __str__(self):
        return self.titulo
