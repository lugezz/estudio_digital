from import_export import resources
from .models import Feriado

class FeriadoResource(resources.ModelResource):
    class Meta:
        model = Feriado
