from rest_framework import serializers

from . import models


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Destination
        fields = [
            'name',
            'disney_id',
            'id'
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = [
            'id',
            'name',
            'disney_id',
            'location_type',
            'destination',
        ]


class LandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Land
        fields = [
            'id',
            'name',
            'disney_id',
            'park',
        ]

    def validate_park(self, value):
        if value.location_type == models.Location.LocationType.RESORT:
            raise serializers.ValidationError(
                "A land's park must be a theme park or a water park."
            )
        return value


class ExperienceSerializer(serializers.ModelSerializer):
    lands = LandSerializer(many=True, read_only=True)  # This will serialize the related Land
    locations = LocationSerializer(many=True, read_only=True)  # This will serialize all related Locations

    class Meta:
        model = models.Experience
        exclude = ['date_created', 'is_deleted', 'date_updated']
