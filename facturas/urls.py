from django.urls import path
from facturas.views import (
    FacturasListView, CreateFacturaView, FacturaDetailView,
    UpdateFacturaView, RemoveFacturaView, ResultadosListView,
    GetFacturasView)

app_name = 'facturas'

urlpatterns = [
    path('list/', FacturasListView.as_view(), name='list'),
    path('list/resultados', ResultadosListView.as_view(), name='resultados'),
    path('create/', CreateFacturaView.as_view(), name='add_factura'),
    path('<int:pk>/view/', FacturaDetailView.as_view(), name="view_factura"),
    path('<int:pk>/edit/', UpdateFacturaView.as_view(), name="edit_factura"),
    path('<int:pk>/delete/',
         RemoveFacturaView.as_view(),
         name="remove_factura"),

    path('get/list/', GetFacturasView.as_view(), name="get_facturas"),

]
