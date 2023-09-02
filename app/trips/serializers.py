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
        trip = models.Trip.objects.create(destination=destination_id, **validated_data)
        return trip


class BreakSerializer(serializers.ModelSerializer):
    location = dest_serializers.LocationSerializer()

    class Meta:
        model = models.Break
        exclude = ['date_created', 'is_deleted', 'date_updated']


class TravelEventSerializer(serializers.ModelSerializer):
    from_location = dest_serializers.LocationSerializer()
    to_location = dest_serializers.LocationSerializer()
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
    meal_experience = dest_serializers.ExperienceSerializer(read_only=True)
    meal_experience_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = models.Meal
        fields = ['id', 'meal_experience', 'meal_experience_id', 'meal_type']

    # def create(self, validated_data):
    #     print("in meal create")
    #     meal_experience_id = validated_data.pop('meal_experience_id', None)
    #
    #     if meal_experience_id:
    #         meal_experience = dest_models.Experience.objects.get(pk=meal_experience_id)
    #         validated_data['meal_experience'] = meal_experience
    #
    #     return super().create(validated_data)


class ContentTypeField(serializers.RelatedField):
    def to_representation(self, value):
        return value.model

    def to_internal_value(self, data):
        return ContentType.objects.get(model=data)


class ItineraryItemSerializer(serializers.ModelSerializer):
    activity = serializers.JSONField(required=False)  # Add this line
    content_type_id = serializers.IntegerField(read_only=True)
    # content_type = ContentTypeField(queryset=ContentType.objects.all())
    activity_id = serializers.UUIDField(required=False)
    content_type = ContentTypeField(queryset=ContentType.objects.all(), required=False)

    class Meta:
        model = models.ItineraryItem
        exclude = ['date_created', 'is_deleted', 'date_updated']

    def validate(self, data):
        # print('in validate')
        http_method = self.context.get('http_method')
        content_type = data.get('content_type')

        # Validate content_type
        if content_type:
            data['content_type_id'] = content_type.id  # Add content_type_id to validated_data

            # Other validations when content_type is not None
            if content_type.model == 'note':
                if 'notes' not in data or not data['notes']:
                    raise serializers.ValidationError({'notes': 'The notes field is required for content_type "note".'})
            elif content_type.model == 'experience':
                if not data.get('activity_id'):
                    raise serializers.ValidationError({'activity_id': 'This field is required for experiences.'})
            elif content_type.model not in ['experience', 'note']:
                if http_method == 'POST':
                    if not data.get('activity'):  # You could add other checks here
                        raise serializers.ValidationError(
                            {
                                'activity': 'This field is required for all content types except experience when creating.'})
                elif http_method == 'PUT':
                    if not data.get('activity_id'):  # Here, activity_id is needed
                        raise serializers.ValidationError(
                            {
                                'activity_id': 'This field is required for all content types except experience when updating.'})
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
        return super().to_representation(instance)

    def create(self, validated_data):
        print(f"validated_data: {validated_data}")
        content_type = validated_data.pop('content_type', None)
        activity = validated_data.pop('activity', None)

        # If content_type is 'note', handle it differently
        if not content_type:
            # validated_data['notes'] = validated_data.pop('activity', {}).get('notes')
            notes = validated_data.pop('notes', '')
            print('popped notes:', notes)
            itinerary_item = models.ItineraryItem.objects.create(notes=notes, **validated_data)
            return itinerary_item


        # Create the activity based on the content type
        if content_type.model == 'meal':
            meal_experience_id = activity.get('meal_experience_id')
            activity['meal_experience_id'] = meal_experience_id
            activity_obj = models.Meal.objects.create(**activity)
        elif content_type.model == 'break':
            try:
                location_instance = dest_models.Location.objects.get(id=activity['location'])
                activity_obj = models.Break.objects.create(location=location_instance)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Location does not exist.")
        elif content_type.model == 'travelevent':
            try:
                from_location_instance = dest_models.Location.objects.get(id=activity['from_location'])
                to_location_instance = dest_models.Location.objects.get(id=activity['to_location'])
                activity_obj = models.TravelEvent.objects.create(
                    from_location=from_location_instance,
                    to_location=to_location_instance
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Location does not exist.")
            # activity_obj = models.TravelEvent.objects.create(**activity)
        elif content_type.model == 'experience':
            activity_id = validated_data.get('activity_id')
            if not dest_models.Experience.objects.filter(id=activity_id).exists():
                raise serializers.ValidationError("Invalid experience_id provided.")
            activity_obj = dest_models.Experience.objects.get(id=activity_id)
        else:
            raise serializers.ValidationError('Invalid activity type')
        # print('turtles', activity_obj)
        validated_data['activity_id'] = activity_obj.id
        validated_data['content_type_id'] = content_type.id

        # Create the itinerary item
        itinerary_item = models.ItineraryItem.objects.create(**validated_data)
        return itinerary_item

    def update(self, instance, validated_data):
        # print('in update')
        if instance.content_type is None:
            instance.notes = validated_data.get('notes', instance.notes)
            instance.save()
            return instance

        try:
            trip_id = self.context.get('trip_id')

            if instance.trip.id != trip_id:
                raise serializers.ValidationError(
                    f"Mismatch between trip_id in URL and the ItineraryItem's associated trip."
                )

            # Handle activity updates here if needed
            activity_data = validated_data.pop('activity', None)

            if activity_data:
                if instance.content_type.model == 'meal':
                    models.Meal.objects.filter(id=instance.activity_id).update(**activity_data)
                elif instance.content_type.model == 'break':
                    models.Break.objects.filter(id=instance.activity_id).update(**activity_data)
                elif instance.content_type.model == 'travelevent':
                    models.TravelEvent.objects.filter(id=instance.activity_id).update(**activity_data)
                elif instance.content_type.model == 'experience':
                    # No updates for Experience as they are immutable
                    pass

            instance = super().update(instance, validated_data)
            instance.save()

            return instance

        except Exception as e:
            raise serializers.ValidationError(f"An error occurred: {str(e)}")

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
        print("in update")
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
