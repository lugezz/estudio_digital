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
    path('<int:pk>/', NovedadDetailView.as_view(), name='novedad-detail'),
    path('<int:pk>/actualizar/', NovedadUpdateView.as_view(), name='novedad-update'),
    path('<int:pk>/eliminar/', NovedadDeleteView.as_view(), name='novedad-delete'),
]
