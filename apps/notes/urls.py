from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('courbe/', views.courbe, name='courbe'),
    path('<int:module_choisi_id>/', views.saisie_notes, name='saisie_notes'),
]
