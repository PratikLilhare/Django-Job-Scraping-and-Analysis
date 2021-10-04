from django.urls import path
from . import views

urlpatterns = [
    path('', views.show),
    path('plot-image/', views.plot_image),
]
