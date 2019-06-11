from django import forms
from import_export.forms import ConfirmImportForm, ImportForm

from .models import Feriado, GanArt23, GanArt90

class FeriadoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FeriadoForm, self).__init__(*args, **kwargs)

        for key, value in self.fields.items():
            if key == 'fecha':
                value.widget.attrs['placeholder'] = "dd/mm/aaaa"
            else:
                value.widget.attrs['placeholder'] = value.label

    class Meta:
        model = Feriado
        fields = ['nombre', 'fecha']

    fecha = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'datepicker'}),
            input_formats=('%d/%m/%Y', )
        )
