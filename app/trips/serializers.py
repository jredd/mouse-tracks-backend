from rest_framework import serializers
from . import models
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from destinations import serializers as dest_serializers
from destinations import models as dest_models


class TripSerializer(serializers.ModelSerializer):
    destination = dest_serializers.DestinationSerializer(read_only=True)
    destination_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = models.Trip
        exclude = ['date_created', 'is_deleted', 'date_updated']

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after the start date.")
        return data

    def create(self, validated_data):
        destination_id = validated_data.pop('destination_id')
        destination_instance = dest_models.Destination.objects.get(pk=destination_id)
        trip = models.Trip.objects.create(destination=destination_instance, **validated_data)
        return trip


class BreakSerializer(serializers.ModelSerializer):
    location = dest_serializers.LocationSerializer(read_only=True)
    location_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = models.Break
        exclude = ['date_created', 'is_deleted', 'date_updated']


class TravelEventSerializer(serializers.ModelSerializer):
    from_location = dest_serializers.LocationSerializer(read_only=True)
    to_location = dest_serializers.LocationSerializer(read_only=True)

    from_location_id = serializers.UUIDField(write_only=True)
    to_location_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = models.TravelEvent
        exclude = ['date_created', 'is_deleted', 'date_updated']


class MealSerializer(serializers.ModelSerializer):
    meal_experience = dest_serializers.ExperienceSerializer(read_only=True)
    meal_experience_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = models.Meal
        fields = ['id', 'meal_experience', 'meal_experience_id', 'meal_type']


class ContentTypeField(serializers.RelatedField):
    def to_representation(self, value):
        if value is None:
            return 'note'
        return value.model

    def to_internal_value(self, data):
        if data == 'note':
            return None
        return ContentType.objects.get(model=data)


class ItineraryItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False, required=False)
    # id = serializers.UUIDField(read_only=True, required=False)
    activity = serializers.JSONField(required=False)  # Add this line
    content_type_id = serializers.IntegerField(read_only=True)
    activity_id = serializers.UUIDField(required=False, allow_null=True)
    content_type = ContentTypeField(queryset=ContentType.objects.all(), required=False)

    class Meta:
        model = models.ItineraryItem
        fields = [
            'id',
            'trip',
            'notes',
            'activity_order',
            'start_time',
            'end_time',
            'day',
            'activity_id',
            'content_type',
            'content_type_id',
            'activity',
            'attributes'
        ]

    def validate(self, data):
        # print('in validate')
        http_method = self.context.get('http_method')
        content_type = data.get('content_type')

        # Validate content_type
        if content_type:
            data['content_type_id'] = content_type.id  # Add content_type_id to validated_data

            # Other validations when content_type is not None
            if content_type is None:
                if 'notes' not in data or not data['notes']:
                    raise serializers.ValidationError({'notes': 'The notes field is required when content_type is "note".'})
            elif content_type.model == 'experience':
                if not data.get('activity_id'):
                    raise serializers.ValidationError({'activity_id': 'This field is required for experiences.'})

            elif content_type.model not in ['experience', 'note']:
                if http_method == 'POST':
                    if not data.get('activity'):  # You could add other checks here
                        raise serializers.ValidationError(
                            {
                                'activity': 'This field is required for all content types except experience when creating.'})
                    if data.get('id'):
                        raise serializers.ValidationError(
                            {
                                'id': 'This breaks unique constraint on the table.'})
                elif http_method == 'PUT':
                    if not data.get('activity_id'):  # Here, activity_id is needed
                        raise serializers.ValidationError(
                            {
                                'activity_id': 'This field is required for all content types except experience when updating.'})
                    if not data.get('id'):  # Here, id is needed
                        raise serializers.ValidationError(
                            {
                                'id': 'The pk field is required for put actions'})
        else:
            # Handle case where content_type is None (assumed to be notes)
            if 'notes' not in data or not data['notes']:
                raise serializers.ValidationError(
                    {'notes': 'The notes field is required when content_type is not provided.'})

        # Validate trip_id
        trip_id = self.context.get('trip_id')
        if 'trip' in data and data['trip'].id != trip_id:
            raise serializers.ValidationError(
                f"Mismatch between trip_id in URL and trip_id in request body for record {data.get('id', 'unknown')}."
            )

        return data

    def to_representation(self, instance):
        self.fields['activity'] = serializers.SerializerMethodField()

        representation = super().to_representation(instance)

        if representation['content_type'] is None:
            representation['content_type'] = "note"

        return representation

    def create(self, validated_data):
        print(f"validated_data: {validated_data}")
        content_type = validated_data.pop('content_type', None)
        activity = validated_data.pop('activity', None)

        # If content_type is 'note', handle it differently
        if not content_type:
            notes = validated_data.pop('notes', '')
            itinerary_item = models.ItineraryItem.objects.create(notes=notes, **validated_data)
            return itinerary_item

        # Create the activity based on the content type
        if content_type.model == 'meal':
            activity_obj = models.Meal.objects.create(**activity)
        elif content_type.model == 'break':
            try:
                location_instance = dest_models.Location.objects.get(id=activity['location'])
                activity_obj = models.Break.objects.create(location=location_instance)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Location does not exist.")
        elif content_type.model == 'travelevent':
            from_location_instance = None
            to_location_instance = None

            # Check if from_location_id and to_location_id are provided, and if so, fetch them.
            if activity.get('from_location_id'):
                try:
                    from_location_instance = dest_models.Location.objects.get(id=activity.pop('from_location_id'))
                    activity['from_location'] = from_location_instance
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("From location does not exist.")

            if activity.get('to_location_id'):
                try:
                    to_location_instance = dest_models.Location.objects.get(id=activity.pop('to_location_id'))
                    activity['to_location'] = to_location_instance
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("To location does not exist.")

            # If neither location ID nor custom location is provided, raise an error.
            if not from_location_instance and not activity.get('custom_from_location'):
                raise serializers.ValidationError("Either from_location_id or custom_from_location must be provided.")

            if not to_location_instance and not activity.get('custom_to_location'):
                raise serializers.ValidationError("Either to_location_id or custom_to_location must be provided.")

            activity_obj = models.TravelEvent.objects.create(**activity)

        elif content_type.model == 'experience':
            activity_id = validated_data.get('activity_id')
            if not dest_models.Experience.objects.filter(id=activity_id).exists():
                raise serializers.ValidationError("Invalid experience_id provided.")
            activity_obj = dest_models.Experience.objects.get(id=activity_id)
        else:
            raise serializers.ValidationError('Invalid activity type')

        validated_data['activity_id'] = activity_obj.id
        validated_data['content_type_id'] = content_type.id

        # Create the itinerary item
        itinerary_item = models.ItineraryItem.objects.create(**validated_data)
        return itinerary_item

    def update(self, instance, validated_data):
        # Ensure the trip_id matches the instance's trip.
        trip_id = self.context.get('trip_id')
        if instance.trip.id != trip_id:
            raise serializers.ValidationError(
                "Mismatch between trip_id in URL and the ItineraryItem's associated trip."
            )

        # We don't want to modify the activity directly
        activity_data = validated_data.pop('activity', None)

        # If instance's content_type is None, handle it as a special case for notes.
        if instance.content_type is None or instance.content_type.model == 'note':
            instance = super().update(instance, validated_data)
            return instance

        if activity_data:
            # Update the activity model corresponding to the instance's content_type.
            if instance.content_type.model == 'meal':
                models.Meal.objects.filter(id=instance.activity_id).update(**activity_data)
            elif instance.content_type.model == 'break':
                models.Break.objects.filter(id=instance.activity_id).update(**activity_data)
            elif instance.content_type.model == 'travelevent':
                models.TravelEvent.objects.filter(id=instance.activity_id).update(**activity_data)
            elif instance.content_type.model == 'experience':
                # No updates for Experience as they are immutable.
                pass
            else:
                # If we encounter an unknown content_type.model, raise an error.
                raise serializers.ValidationError('Unknown activity type encountered during update.')

        instance = super().update(instance, validated_data)

        return instance

    def get_activity(self, obj):
        if obj.activity is None or obj.content_type is None:
            return None

        if isinstance(obj.activity, dest_models.Experience):
            return dest_serializers.ExperienceSerializer(obj.activity).data
        elif isinstance(obj.activity, models.Break):
            return BreakSerializer(obj.activity).data
        elif isinstance(obj.activity, models.TravelEvent):
            return TravelEventSerializer(obj.activity).data
        elif isinstance(obj.activity, models.Meal):
            return MealSerializer(obj.activity).data
        return None


class ItineraryItemsBulkSerializer(serializers.ListSerializer):
    child = ItineraryItemSerializer()

    def create(self, validated_data):
        print("Bulk create method called")
        # print(f"bulk validated_data: {validated_data}")
        # Using Django's transaction.atomic to ensure atomic transactions
        with transaction.atomic():
            items = []
            for item_data in validated_data:
                item = self.child.create(item_data)
                items.append(item)
            return items

    def update(self, instances, validated_data):
        print("Bulk update method called")
        updated_instances = []

        for attrs in validated_data:
            instance = next(i for i in instances if i.id == attrs['id'])

            # Use the singleton serializer (child) to handle the update
            serializer = self.child
            updated_instance = serializer.update(instance, attrs)
            updated_instances.append(updated_instance)

        return updated_instances


class ItineraryItemsBulkDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), read_only=True)

    def to_internal_value(self, data):
        # This method maps the direct list of IDs to the internal structure
        # Expected by the rest of the serializer.
        return {'ids': data}

    def validate_ids(self, value):
        """
        Check that all IDs provided are valid, exist, and belong to the specified trip.
        """
        trip_id = self.context.get('trip_id')
        existing_ids = set(
            models.ItineraryItem.objects.filter(id__in=value, trip_id=trip_id).values_list('id', flat=True))

        if set(value) != existing_ids:
            raise serializers.ValidationError(
                "One or more IDs are invalid, do not exist, or don't belong to the specified trip.")

        return value
