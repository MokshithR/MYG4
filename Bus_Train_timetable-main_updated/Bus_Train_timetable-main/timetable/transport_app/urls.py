from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('search-bus/', views.search_buses, name='search_bus'), 
    path('search-train/', views.search_trains, name='search_train'), 

    path('suggest/', views.suggest_routes, name='suggest_routes'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('contact/', views.contact_us, name='contact_us'),
    path('download-bus-pdf/', views.generate_bus_pdf, name='download_bus_pdf'),
    path('download-train-pdf/', views.generate_train_pdf, name='download_train_pdf'),
]