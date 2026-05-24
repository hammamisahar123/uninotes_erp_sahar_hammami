from django.urls import path
from . import views

app_name = 'inscription'

urlpatterns = [
    path('', views.panier, name='panier'),
    path('ajouter/<int:module_id>/', views.ajouter_module, name='ajouter_module'),
    path('retirer/<int:module_choisi_id>/', views.retirer_module, name='retirer_module'),
]
