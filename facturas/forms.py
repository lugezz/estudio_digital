from django import forms

from .models import IVA

class FacturasForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FacturasForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}

    class Meta:
        model = IVA
        fields = (
            'tipo_iva', 'periodo', 'neto_gravado',
            'neto_no_gravado', 'exento',
            'iva', 'percepcion'
        )
