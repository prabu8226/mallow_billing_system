from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_bill, name='generate_bill'),
    path('history/', views.history, name='history'),
    path('bill/<int:bill_id>/', views.bill_detail, name='bill_detail'),
]
