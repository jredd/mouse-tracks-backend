from rest_framework import permissions
from rest_framework import generics
from . import models, serializers
from common import IsStaffOrSuperuser


class DestinationListView(generics.ListCreateAPIView):
    queryset = models.Destination.objects.all()
    serializer_class = serializers.DestinationSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsStaffOrSuperuser()]
        return [permissions.IsAuthenticated()]


class DestinationDetailView(generics.RetrieveAPIView):
    queryset = models.Destination.objects.all()
    serializer_class = serializers.DestinationSerializer
    permission_classes = [permissions.IsAuthenticated]


class LocationListView(generics.ListCreateAPIView):
    serializer_class = serializers.LocationSerializer

    def get_queryset(self):
        dest_id = self.kwargs['dest_id']
        return models.Location.objects.filter(destination__id=dest_id)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsStaffOrSuperuser()]
        return [permissions.IsAuthenticated()]


class LocationDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Location.objects.filter(id=self.kwargs['pk'], destination__id=self.kwargs['dest_id'])


class LandListView(generics.ListCreateAPIView):
    serializer_class = serializers.LandSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        loc_id = self.kwargs['loc_id']
        return models.Land.objects.filter(park__id=loc_id)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsStaffOrSuperuser()]
        return [permissions.IsAuthenticated()]


class LandDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.LandSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Land.objects.filter(id=self.kwargs['pk'], location__id=self.kwargs['loc_id'])


class ExperienceListView(generics.ListCreateAPIView):
    serializer_class = serializers.ExperienceSerializer

    def get_queryset(self):
        loc_id = self.kwargs['loc_id']
        return models.Experience.objects.filter(locations__id=loc_id)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsStaffOrSuperuser()]
        return [permissions.IsAuthenticated()]


class ExperienceDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Experience.objects.filter(id=self.kwargs['pk'], location__id=self.kwargs['loc_id'])
