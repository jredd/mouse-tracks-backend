from rest_framework import permissions
from rest_framework import generics
from . import models, serializers
from common import StaffRequiredMixin


# class DestinationListView(StaffRequiredMixin, generics.ListCreateAPIView):
class DestinationListView(generics.ListCreateAPIView):
    queryset = models.Destination.objects.all()
    serializer_class = serializers.DestinationSerializer
    # permission_classes = [permissions.IsAuthenticated]

# class DestinationDetailView(StaffRequiredMixin, generics.RetrieveUpdateAPIView):
class DestinationDetailView(generics.RetrieveUpdateAPIView):
    queryset = models.Destination.objects.all()
    serializer_class = serializers.DestinationSerializer
    # permission_classes = [permissions.IsAuthenticated]

# class LocationListView(StaffRequiredMixin, generics.ListCreateAPIView):
class LocationListView(generics.ListCreateAPIView):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    # permission_classes = [permissions.IsAuthenticated]

# class LocationDetailView(StaffRequiredMixin, generics.RetrieveUpdateAPIView):
class LocationDetailView(generics.RetrieveUpdateAPIView):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    # permission_classes = [permissions.IsAuthenticated]

# class LandListView(StaffRequiredMixin, generics.ListCreateAPIView):
class LandListView(generics.ListCreateAPIView):
    queryset = models.Land.objects.all()
    serializer_class = serializers.LandSerializer
    # permission_classes = [permissions.IsAuthenticated]

# class LandDetailView(StaffRequiredMixin, generics.RetrieveUpdateAPIView):
class LandDetailView(generics.RetrieveUpdateAPIView):
    queryset = models.Land.objects.all()
    serializer_class = serializers.LandSerializer
    # permission_classes = [permissions.IsAuthenticated]

# class ExperienceListView(StaffRequiredMixin, generics.ListCreateAPIView):
class ExperienceListView(generics.ListCreateAPIView):
    queryset = models.Experience.objects.all()
    serializer_class = serializers.ExperienceSerializer
    # permission_classes = [permissions.IsAuthenticated]

# class ExperienceDetailView(StaffRequiredMixin, generics.RetrieveUpdateAPIView):
class ExperienceDetailView(generics.RetrieveUpdateAPIView):
    queryset = models.Experience.objects.all()
    serializer_class = serializers.ExperienceSerializer
    # permission_classes = [permissions.IsAuthenticated]
