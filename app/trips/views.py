from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError

from . import models
from . import serializers
from . import filters as filters


class TripView(viewsets.ModelViewSet):
    serializer_class = serializers.TripSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the trips
        for the currently authenticated user, or for staff/admin.
        """
        # user = self.request.user
        # if user.is_staff or user.is_superuser:
        #     return models.Trip.objects.all()
        # return models.Trip.objects.filter(created_by=user)
        user_uuid = "928a9da6-fd89-4b1b-9f78-4d6fcfee3038"
        User = get_user_model()
        user = User.objects.get(id=user_uuid)
        return models.Trip.objects.filter(created_by=user)


    def perform_create(self, serializer):
        user_uuid = "928a9da6-fd89-4b1b-9f78-4d6fcfee3038"
        User = get_user_model()
        user = User.objects.get(id=user_uuid)
        serializer.save(created_by=user)
        # serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ItineraryItemView(viewsets.ModelViewSet):
    serializer_class = serializers.ItineraryItemSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.ItineraryItemFilter

    def update_itinerary_item(self, instance):
        # Then update the last_content_update of the parent Trip
        trip = instance.trip
        trip.last_content_update = timezone.now()
        trip.save()

    def get_content_type_from_activity_content_type(self, activity_content_type):
        try:
            content_type = ContentType.objects.get(model=activity_content_type.lower())
            return content_type
        except ContentType.DoesNotExist:
            raise ValueError(f"Invalid activity_content_type: {activity_content_type}")

    def get_queryset(self):
        # user = self.request.user
        user_uuid = "928a9da6-fd89-4b1b-9f78-4d6fcfee3038"
        User = get_user_model()
        user = User.objects.get(id=user_uuid)
        trip_id = self.kwargs.get('trip_id')
        if trip_id is not None:
            return models.ItineraryItem.objects.filter(trip__id=trip_id, trip__created_by=user)
        return models.ItineraryItem.objects.filter(trip__created_by=user)

    def create(self, request, *args, **kwargs):
        serializer_data = request.data.copy()
        activity_content_type = serializer_data.get('activity_content_type')
        if not activity_content_type:
            return Response({"detail": "activity_content_type is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = self.get_content_type_from_activity_content_type(activity_content_type)
            serializer_data[
                'content_type_id'] = content_type.id  # This should match the expected field in the serializer
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if serializer.instance:
            self.update_itinerary_item(serializer.instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        response = super().update(request, *args, **kwargs)

        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            self.update_itinerary_item(instance)

        return response

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        response = super().partial_update(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            self.update_itinerary_item(instance)

        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        trip = instance.trip
        response = super().destroy(request, *args, **kwargs)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.update_itinerary_item(trip)

#         return response


class ItineraryItemBulkView(APIView):

    def check_items_permissions(self, request, item_ids):
        """
        Check permissions for a list of itinerary items.
        """
        items = models.ItineraryItem.objects.filter(id__in=item_ids)

        if len(item_ids) != items.count():
            raise NotFound("One or more items were not found.")

        for item in items:
            if item.itinerary_item.trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
                self.permission_denied(request)

    def check_trips_permissions(self, request, trip_ids):
        """
        Check permissions for a list of trips.
        """
        trips = models.Trip.objects.filter(id__in=trip_ids)

        if len(trip_ids) != trips.count():
            raise NotFound("One or more trips were not found.")

        for trip in trips:
            if trip.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
                self.permission_denied(request)

    def post(self, request, trip_id):
        print("Post method called")
        print("request data:", request.data)
        # serializer = serializers.ItineraryItemsBulkSerializer(data=request.data, context={'trip_id': trip_id})
        serializer = serializers.ItineraryItemsBulkSerializer(
            data=request.data,
            context={'trip_id': trip_id, 'http_method': 'POST'}
        )

        # print("Serializer Errors:", serializer.errors)
        if not serializer.is_valid():
            print('errors:', serializer.errors)
        with transaction.atomic():
            if serializer.is_valid(raise_exception=True):
                print("Serialized Data:", serializer.initial_data)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, trip_id):
        if not all("id" in item_data for item_data in request.data):
            raise ValidationError("All items must contain an 'id' for updating.")
        # self.check_items_permissions(request, item_ids)

        with transaction.atomic():
            updated_items = []
            for item_data in request.data:
                item_instance = models.ItineraryItem.objects.get(id=item_data["id"])
                # serializer = serializers.ItineraryItemSerializer(item_instance, data=item_data, partial=True,
                #                                                  context={'trip_id': trip_id})
                serializer = serializers.ItineraryItemSerializer(
                    item_instance,
                    data=item_data,
                    partial=True,
                    context={'trip_id': trip_id, 'http_method': 'PUT'}
                )

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    updated_items.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(updated_items, status=status.HTTP_200_OK)

    def delete(self, request, trip_id):
        serializer = serializers.ItineraryItemsBulkDeleteSerializer(data=request.data, context={'trip_id': trip_id})
        if serializer.is_valid(raise_exception=True):
            # Future: Add checks for trip ownership here.

            with transaction.atomic():
                models.ItineraryItem.objects.filter(id__in=serializer.validated_data['ids']).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)


class BaseActivityView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        """
        This view should return a list of all the instances
        for the currently authenticated user, or for staff/admin.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.serializer_class.Meta.model.objects.all()
        return self.serializer_class.Meta.model.objects.filter(itinerary_item__trip__created_by=user)

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
