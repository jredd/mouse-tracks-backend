from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

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


class BreakView(viewsets.ModelViewSet):
    serializer_class = serializers.BreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.BreakFilter

    def get_queryset(self):
        """
        This view should return a list of all the breaks
        for the currently authenticated user, or for staff/admin.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return models.Break.objects.all()
        return models.Break.objects.filter(itinerary_item__trip__created_by=user)

    def perform_create(self, serializer):
        itinerary_item = get_object_or_404(models.ItineraryItem, id=self.kwargs['itinerary_item_pk'])
        serializer.save(itinerary_item=itinerary_item)


class TravelEventView(viewsets.ModelViewSet):
    serializer_class = serializers.TravelEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.TravelEventFilter

    def get_queryset(self):
        """
        This view should return a list of all the travel events
        for the currently authenticated user, or for staff/admin.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return models.TravelEvent.objects.all()
        return models.TravelEvent.objects.filter(itinerary_item__trip__created_by=user)

    def perform_create(self, serializer):
        itinerary_item = get_object_or_404(models.ItineraryItem, id=self.kwargs['itinerary_item_pk'])
        serializer.save(itinerary_item=itinerary_item)
