from django.urls import path
from .views import (
    NovedadCreateView,
    NovedadDeleteView,
    NovedadDetailView,
    NovedadListView,
    NovedadUpdateView,
)

app_name = 'novedades'
urlpatterns = [
    path('', NovedadListView.as_view(), name='novedad-list'),
    path('crear/', NovedadCreateView.as_view(), name='novedad-create'),
    path('<int:id>/', NovedadDetailView.as_view(), name='novedad-detail'),
    path('<int:id>/actualizar/', NovedadUpdateView.as_view(), name='novedad-update'),
    path('<int:id>/eliminar/', NovedadDeleteView.as_view(), name='novedad-delete'),
]
