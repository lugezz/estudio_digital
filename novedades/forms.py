from django import forms
from .models import Novedad


class NovedadModelForm(forms.ModelForm):
    class Meta:
        model = Novedad
        fields =[
            'titulo',
            'contenido',
            'activo',
        ]
