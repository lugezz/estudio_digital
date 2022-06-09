from django import forms
from .models import Novedad

class NovedadModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        asignado_novedades = kwargs.pop('asignado_a', [])
        super(NovedadModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}

        self.fields['contenido'].widget.attrs.update({
            'rows': '15'})
        self.fields['asignado_a'].queryset = asignado_novedades
        self.fields['asignado_a'].required = False

        for key, value in self.fields.items():
            if key == 'contenido':
                value.widget.attrs['placeholder'] = "Contenido"
            elif key == 'publicado':
                value.widget.attrs['placeholder'] = "dd/mm/aaaa"
            else:
                value.widget.attrs['placeholder'] = value.label

    class Meta:
        model = Novedad
        fields =['titulo', 'contenido',
            'imagen', 'publicado', 'asignado_a']

    publicado = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'datepicker'}),
            input_formats=('%d/%m/%Y', )
        )


        #widgets = {'publicado': forms.DateInput(format=('%d/%m/%Y'),
        #    attrs={'class':'myDateClass'})}
