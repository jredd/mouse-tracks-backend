from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from abc import ABC, abstractmethod


from . import models
from . import serializers
from . import filters as filters


class TripView(viewsets.ModelViewSet):
    serializer_class = serializers.TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the trips
        for the currently authenticated user, or for staff/admin.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return models.Trip.objects.all()
        return models.Trip.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ItineraryItemView(viewsets.ModelViewSet):
    serializer_class = serializers.ItineraryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.ItineraryItemFilter

    def get_queryset(self):
        """
        This view should return a list of all the itinerary items
        for the currently authenticated user, or for staff/admin.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return models.ItineraryItem.objects.all()
        return models.ItineraryItem.objects.filter(trip__created_by=user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class BaseActivityView(generics.UpdateAPIView, generics.DestroyAPIView, ABC):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'pk'

    @abstractmethod
    def get_serializer_class(self):
        pass

    def get_queryset(self):
        """
        This view should return a list of all the instances
        for the currently authenticated user, or for staff/admin.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.get_serializer_class().Meta.model.objects.all()
        return self.get_serializer_class().Meta.model.objects.filter(itinerary_item__trip__created_by=user)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))
        return obj

    def check_permissions(self, request):
        super().check_permissions(request)
        instance = self.get_object()
        if instance.itinerary_item.trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
            self.permission_denied(request)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BreakView(BaseActivityView):
    serializer_class = serializers.BreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.BreakFilter


class TravelEventView(BaseActivityView):
    serializer_class = serializers.TravelEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.TravelEventFilter


class MealView(BaseActivityView):
    serializer_class = serializers.MealSerializer
    permission_classes = [permissions.IsAuthenticated]
