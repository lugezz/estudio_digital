from django.urls import path
from .views import (
    HomeView,
    CreateFeriadoView, FeriadoDeleteView, FeriadoDetailView, FeriadosListView, UpdateFeriadoView,
    GanArt23ListView, GanArt90ListView, importar_feriado
)

app_name = 'tablas'

urlpatterns = [
    path('', HomeView.as_view(), name='tablas_home'),

    #Feriados
    path('feriados/', FeriadosListView.as_view(), name='feriados-list'),
    path('feriados/crear/', CreateFeriadoView.as_view(), name='feriado-create'),
    path('feriados/importar/', importar_feriado, name='feriado-import'),
    path('feriados/<int:pk>/', FeriadoDetailView.as_view(), name='feriado-detail'),
    path('feriados/<int:pk>/actualizar/', UpdateFeriadoView.as_view(), name='feriado-update'),
    path('feriados/<int:pk>/eliminar/', FeriadoDeleteView.as_view(), name='feriado-delete'),

    #Ganancias Art. 23
    path('g23/', GanArt23ListView.as_view(), name='ganart23-list'),

    #Ganancias Art. 90
    path('g90/', GanArt90ListView.as_view(), name='ganart90-list'),
]
