import django_filters

from . import models


class ItineraryItemFilter(django_filters.FilterSet):
    trip_id = django_filters.UUIDFilter(field_name='trip__id')

    class Meta:
        model = models.ItineraryItem
        fields = ['trip_id']


class BreakFilter(django_filters.FilterSet):
    itinerary_item_id = django_filters.UUIDFilter(field_name='itinerary_item__id')

    class Meta:
        model = models.Break
        fields = ['itinerary_item_id']


class TravelEventFilter(django_filters.FilterSet):
    itinerary_item_id = django_filters.UUIDFilter(field_name='itinerary_item__id')

    class Meta:
        model = models.TravelEvent
        fields = ['itinerary_item_id']
