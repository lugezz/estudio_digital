from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources

#admin.site.register(Feriado)
admin.site.register(GanArt23)
admin.site.register(GanArt90)

@admin.register(Feriado)
class FeriadoAdmin(ImportExportModelAdmin):
    pass

class FeriadoResource(resources.ModelResource):

    class Meta:
        model = Feriado
        fields = ('nombre', 'fecha',)

        widgets = {'published': {'format': '%d.%m.%Y'},}
