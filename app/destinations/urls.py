from django.urls import path
from . import views

urlpatterns = [
    path('destinations/', views.DestinationListView.as_view(), name='destination-list'),
    path('destinations/<int:pk>/', views.DestinationDetailView.as_view(), name='destination-detail'),
    path('locations/', views.LocationListView.as_view(), name='location-list'),
    path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location-detail'),
    path('lands/', views.LandListView.as_view(), name='land-list'),
    path('lands/<int:pk>/', views.LandDetailView.as_view(), name='land-detail'),
    path('experiences/', views.ExperienceListView.as_view(), name='experience-list'),
    path('experiences/<int:pk>/', views.ExperienceDetailView.as_view(), name='experience-detail'),
]
