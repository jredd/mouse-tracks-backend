from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'trips', views.TripView, basename='trip')

itinerary_router = routers.NestedSimpleRouter(router, r'trips', lookup='trip')
itinerary_router.register(r'itinerary-items', views.ItineraryItemView, basename='trip-itinerary-items')

break_router = routers.NestedSimpleRouter(itinerary_router, r'itinerary-items', lookup='itinerary_item')
break_router.register(r'breaks', views.BreakView, basename='itinerary-item-breaks')

travel_event_router = routers.NestedSimpleRouter(itinerary_router, r'itinerary-items', lookup='itinerary_item')
travel_event_router.register(r'travel-events', views.TravelEventView, basename='itinerary-item-travel-events')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(itinerary_router.urls)),
    path('', include(break_router.urls)),
    path('', include(travel_event_router.urls)),
]
