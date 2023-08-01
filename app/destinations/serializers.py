from rest_framework import serializers

from . import models


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Destination
        exclude = ['date_created']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        exclude = ['date_created']


class LandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Land
        exclude = ['date_created']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Experience
        exclude = ['date_created']
