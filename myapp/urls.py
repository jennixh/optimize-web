from django.urls import path
from . import views

urlpatterns = [
    path('grafico/', views.solve_linear_program, name='solve'),
    path('bigm/', views.solve_bigm, name='solve_bigm'),  
]