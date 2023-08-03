from rest_framework import serializers

from . import models


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Destination
        fields = [
            'name',
            'id'
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = [
            'id',
            'name',
            'location_type',
            'destination',
        ]


class LandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Land
        fields = [
            'id',
            'name',
            'park',
        ]

    def validate_park(self, value):
        if value.location_type == models.Location.LocationType.RESORT:
            raise serializers.ValidationError(
                "A land's park must be a theme park or a water park."
            )
        return value


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Experience
        exclude = ['date_created', 'is_deleted', 'date_updated']
