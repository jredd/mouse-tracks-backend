from rest_framework import viewsets, permissions

from . import models, serializers
from common import StaffRequiredMixin


class DestinationView(StaffRequiredMixin, viewsets.ModelViewSet):
    queryset = models.Destination.objects.all()
    serializer_class = serializers.DestinationSerializer
    permission_classes = [permissions.IsAuthenticated]


class LocationView(viewsets.ModelViewSet):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    # permission_classes = [permissions.IsAuthenticated]


class LandView(StaffRequiredMixin, viewsets.ModelViewSet):
    queryset = models.Land.objects.all()
    serializer_class = serializers.LandSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExperienceView(StaffRequiredMixin, viewsets.ModelViewSet):
    queryset = models.Experience.objects.all()
    serializer_class = serializers.ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

