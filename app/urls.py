from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name="app-start"),
    path('go/', views.startpayment, name="app-startPayment"),
]
