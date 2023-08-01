from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'destinations', views.DestinationView, basename='destination')
router.register(r'locations', views.LocationView, basename='location')
router.register(r'lands', views.LandView, basename='land')
router.register(r'experiences', views.ExperienceView, basename='experience')

urlpatterns = [
    path('', include(router.urls)),
]
