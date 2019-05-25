from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth import views
from django.urls import include, path
from common.views import handler404, handler500

app_name = 'crm'

urlpatterns = [
    path('', include('common.urls', namespace="common")),
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('contacts/', include('contacts.urls', namespace="contacts")),
    path('facturas/', include('facturas.urls', namespace="facturas")),
    path('logout/', views.LogoutView, {'next_page': '/login/'}, name="logout"),
]
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = handler404
handler500 = handler500
