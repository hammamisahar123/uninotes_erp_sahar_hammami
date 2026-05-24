from django.urls import path, include
from apps.accounts import views as accounts_views
from .admin_site import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', accounts_views.home, name='home'),
    path('', include('apps.accounts.urls')),
    path('panier/', include('apps.inscription.urls')),
    path('notes/', include('apps.notes.urls')),
    path('catalogue/', include('apps.catalogue.urls')),
]
