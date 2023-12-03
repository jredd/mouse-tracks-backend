from rest_framework import permissions
from rest_framework import generics
from . import models, serializers
from common import StaffRequiredMixin


# class DestinationListView(StaffRequiredMixin, generics.ListCreateAPIView):
class DestinationListView(generics.ListCreateAPIView):
    queryset = models.Destination.objects.all()
    serializer_class = serializers.DestinationSerializer
    permission_classes = [permissions.IsAuthenticated]


# class DestinationDetailView(StaffRequiredMixin, generics.RetrieveUpdateAPIView):
class DestinationDetailView(generics.RetrieveUpdateAPIView):
    queryset = models.Destination.objects.all()
    serializer_class = serializers.DestinationSerializer
    permission_classes = [permissions.IsAuthenticated]


# class LocationListView(StaffRequiredMixin, generics.ListCreateAPIView):
class LocationListView(generics.ListCreateAPIView):
    serializer_class = serializers.LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        dest_id = self.kwargs['dest_id']
        return models.Location.objects.filter(destination__id=dest_id)


# class LocationDetailView(StaffRequiredMixin, generics.RetrieveUpdateAPIView):
class LocationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Location.objects.filter(id=self.kwargs['pk'], destination__id=self.kwargs['dest_id'])


# class LandListView(StaffRequiredMixin, generics.ListCreateAPIView):
class LandListView(generics.ListCreateAPIView):
    serializer_class = serializers.LandSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        loc_id = self.kwargs['loc_id']
        return models.Land.objects.filter(park__id=loc_id)


# class LandDetailView(StaffRequiredMixin, generics.RetrieveUpdateAPIView):
class LandDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.LandSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Land.objects.filter(id=self.kwargs['pk'], location__id=self.kwargs['loc_id'])


# class ExperienceListView(StaffRequiredMixin, generics.ListCreateAPIView):
class ExperienceListView(generics.ListCreateAPIView):
    serializer_class = serializers.ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        loc_id = self.kwargs['loc_id']
        return models.Experience.objects.filter(locations__id=loc_id)


# class ExperienceDetailView(StaffRequiredMixin, generics.RetrieveUpdateAPIView):
class ExperienceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Experience.objects.filter(id=self.kwargs['pk'], location__id=self.kwargs['loc_id'])
