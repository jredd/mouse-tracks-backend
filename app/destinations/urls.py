from django.urls import path
from . import views

urlpatterns = [
    path('destinations/', views.DestinationListView.as_view(), name='destination-list'),
    path('destinations/<uuid:dest_id>/', views.DestinationDetailView.as_view(), name='destination-detail'),

    # For locations, lands and experiences, the URLs are nested under the associated destination
    path('destinations/<uuid:dest_id>/locations/', views.LocationListView.as_view(), name='location-list'),
    path('destinations/<uuid:dest_id>/locations/<uuid:loc_id>/', views.LocationDetailView.as_view(), name='location-detail'),

    # For lands, the URLs are nested under the associated location
    path('locations/<uuid:loc_id>/lands/', views.LandListView.as_view(), name='land-list'),
    path('locations/<uuid:loc_id>/lands/<uuid:land_id>/', views.LandDetailView.as_view(), name='land-detail'),

    # For experiences, the URLs are nested under the associated location
    path('experiences/', views.ExperienceListView.as_view(), name='experience-create'),
    path('locations/<uuid:loc_id>/experiences/', views.ExperienceListView.as_view(), name='experience-list'),
    path('locations/<uuid:loc_id>/experiences/<uuid:exp_id>/', views.ExperienceDetailView.as_view(), name='experience-detail'),
]
