from django.urls import path
from . import views

urlpatterns = [
    path('trips/', views.TripView.as_view({'get': 'list', 'post': 'create'}), name='trip-list'),
    path(
        'trips/<int:pk>/',
        views.TripView.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='trip-detail'
    ),
    path(
        'itinerary-items/',
        views.ItineraryItemView.as_view({'get': 'list', 'post': 'create'}),
        name='itinerary-item-list'
    ),
    path(
        'itinerary-items/<int:pk>/',
        views.ItineraryItemView.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='itinerary-item-detail'
    ),
    path('breaks/<int:pk>/', views.BreakView.as_view(), name='break-detail'),
    path('travel-events/<int:pk>/', views.TravelEventView.as_view(), name='travel-event-detail'),
    path('meals/<int:pk>/', views.MealView.as_view(), name='meal-detail'),
]
