from rest_framework import serializers
from . import models
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from destinations.serializers import ExperienceSerializer
from destinations import models as dest_models


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trip
        exclude = ['date_created', 'is_deleted', 'date_updated']

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after the start date.")
        return data


class BreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Break
        exclude = ['date_created', 'is_deleted', 'date_updated']


class TravelEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TravelEvent
        exclude = ['date_created', 'is_deleted', 'date_updated']

    def validate(self, data):
        # Check for from_location fields
        if bool(data.get('from_location')) == bool(data.get('custom_from_location')):
            raise serializers.ValidationError(
                'Only one of from_location and custom_from_location should be filled.'
            )

        # Check for to_location fields
        if bool(data.get('to_location')) == bool(data.get('custom_to_location')):
            raise serializers.ValidationError(
                'Only one of to_location and custom_to_location should be filled.'
            )

        return data


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Meal
        fields = ['id', 'meal_experience', 'meal_type']


class ContentTypeField(serializers.RelatedField):
    def to_representation(self, value):
        return value.model

    def to_internal_value(self, data):
        return ContentType.objects.get(model=data)


class ItineraryItemSerializer(serializers.ModelSerializer):
    activity_content_type = ContentTypeField(queryset=ContentType.objects.all(), source='content_type')
    activity_id = serializers.IntegerField(source='activity_id')
    activity_data = serializers.DictField(write_only=True)

    class Meta:
        model = models.ItineraryItem
        exclude = ['date_created', 'is_deleted', 'date_updated']

    def to_representation(self, instance):
        self.fields['activity'] = serializers.SerializerMethodField()
        return super().to_representation(instance)

    def create(self, validated_data):
        with transaction.atomic():  # Start a new transaction
            activity_content_type = validated_data.pop('content_type')
            activity_data = validated_data.pop('activity_data')

            # Add validation for the different types of activities
            if activity_content_type.model == 'meal':
                activity_serializer = MealSerializer(data=activity_data)
            elif activity_content_type.model == 'experience':
                activity_serializer = ExperienceSerializer(data=activity_data)
            elif activity_content_type.model == 'break':
                activity_serializer = BreakSerializer(data=activity_data)
            elif activity_content_type.model == 'travelevent':
                activity_serializer = TravelEventSerializer(data=activity_data)
            else:
                raise serializers.ValidationError('Invalid activity type')

            # Validate the activity data using the corresponding serializer
            activity_serializer.is_valid(raise_exception=True)
            activity = activity_serializer.save()

            validated_data['activity_id'] = activity.id
            return super().create(validated_data)

    def get_activity(self, obj):
        if isinstance(obj.activity, dest_models.Experience):
            return ExperienceSerializer(obj.activity).data
        elif isinstance(obj.activity, models.Break):
            return BreakSerializer(obj.activity).data
        elif isinstance(obj.activity, models.TravelEvent):
            return TravelEventSerializer(obj.activity).data
        elif isinstance(obj.activity, models.Meal):
            return MealSerializer(obj.activity).data
        return None
