from django.urls import path
from . import views

urlpatterns = [
    path('trips/', views.TripView.as_view({'get': 'list', 'post': 'create'}), name='trip-list'),
    path('trips/<uuid:pk>/', views.TripView.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='trip-detail'),
    path('trips/<uuid:trip_id>/itinerary-items/',
         views.ItineraryItemView.as_view({'get': 'list', 'post': 'create'}),
         name='itinerary-item-list'),
    path('trips/<uuid:trip_id>/itinerary-items-bulk/',
         views.ItineraryItemBulkView.as_view(),
         name='itinerary-items-bulk'),
    path('itinerary-items/<uuid:pk>/', views.ItineraryItemView.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='itinerary-item-detail'),
    path('itinerary-items/<uuid:itinerary_item_pk>/breaks/<uuid:pk>/', views.BreakView.as_view(), name='break-detail'),
    path('itinerary-items/<uuid:itinerary_item_pk>/travel-events/<uuid:pk>/', views.TravelEventView.as_view(),
         name='travel-event-detail'),
    path('itinerary-items/<uuid:itinerary_item_pk>/meals/<uuid:pk>/', views.MealView.as_view(), name='meal-detail'),
]
