from rest_framework import serializers
from . import models
from django.contrib.contenttypes.models import ContentType

from destinations.serializers import ExperienceSerializer
from destinations import models as dest_models


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trip
        exclude = ['date_created']


class BreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Break
        exclude = ['date_created']


class TravelEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TravelEvent
        exclude = ['date_created']


class ContentTypeField(serializers.RelatedField):
    def to_representation(self, value):
        return value.model

    def to_internal_value(self, data):
        return ContentType.objects.get(model=data)


class ItineraryItemSerializer(serializers.ModelSerializer):
    activity_content_type = ContentTypeField(queryset=ContentType.objects.all(), source='content_type')
    activity_id = serializers.IntegerField(source='activity_id')

    class Meta:
        model = models.ItineraryItem
        exclude = ['date_created']

    def to_representation(self, instance):
        self.fields['activity'] = serializers.SerializerMethodField()
        return super().to_representation(instance)

    def get_activity(self, obj):
        if isinstance(obj.activity, dest_models.Experience):
            return ExperienceSerializer(obj.activity).data
        elif isinstance(obj.activity, models.Break):
            return BreakSerializer(obj.activity).data
        elif isinstance(obj.activity, models.TravelEvent):
            return TravelEventSerializer(obj.activity).data
        return None

