from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from common import BaseModel
from destinations import models as dest_models
from custom_auth.models import User


VALID_CONTENT_TYPES = {'experience', 'break', 'travelevent', 'meal'}


class Trip(BaseModel):
    title = models.CharField(max_length=150, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(dest_models.Destination, on_delete=models.CASCADE)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    last_content_update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_by.first_name}'s:{self.title}"

    def clean(self):
        super().clean()

        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({
                'end_date': 'End date must be after the start date.',
            })


class Break(BaseModel):
    location = models.ForeignKey(dest_models.Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"Break: {self.location.name}"


class TravelEvent(BaseModel):
    class EventType(models.TextChoices):
        CHECK_IN = "check-in"
        CHECK_OUT = "check-out"
        PARK_HOP = "park-hop"
        OTHER_TRAVEL = "other-travel"

    from_location = models.ForeignKey(
        dest_models.Location, related_name='travels_from', blank=True, null=True, on_delete=models.SET_NULL
    )
    to_location = models.ForeignKey(
        dest_models.Location, related_name='travels_to', blank=True, null=True, on_delete=models.SET_NULL
    )
    custom_from_location = models.CharField(max_length=200, blank=True, null=True)
    custom_to_location = models.CharField(max_length=200, blank=True, null=True)
    travel_type = models.CharField(
        max_length=12,
        choices=EventType.choices,
        blank=False,
    )

    def __str__(self):
        return (
            f"Travel event ({self.get_travel_type_display()}): "
            f"{self.from_location or self.custom_from_location} -> "
            f"{self.to_location or self.custom_to_location}"
        )

    def clean(self):
        super().clean()

        # Check for from_location fields
        if bool(self.from_location) == bool(self.custom_from_location):
            raise ValidationError(
                'Only one of from_location and custom_from_location should be filled.'
            )

        # Check for to_location fields
        if bool(self.to_location) == bool(self.custom_to_location):
            raise ValidationError(
                'Only one of to_location and custom_to_location should be filled.'
            )


class Meal(BaseModel):
    class MealType(models.TextChoices):
        BREAKFAST = "breakfast"
        LUNCH = "lunch"
        DINNER = "dinner"
        SNACK = "snack"

    meal_experience = models.ForeignKey(dest_models.Experience, on_delete=models.CASCADE)
    meal_type = models.CharField(
        max_length=20,
        choices=MealType.choices,
        blank=False,
    )

    def __str__(self):
        return f"{self.meal_type}: {self.meal_experience.name}"


class ItineraryItem(BaseModel):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    notes = models.CharField(max_length=800, blank=True, null=True)
    activity_order = models.IntegerField(blank=False)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    day = models.DateField(blank=False)

    # Fields for generic relation
    activity_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    activity = GenericForeignKey('content_type', 'activity_id')

    def __str__(self):
        return f"{self.day}:{self.activity_order}"

    def clean(self):
        super().clean()
        if self.content_type.model not in VALID_CONTENT_TYPES:
            raise ValidationError(
                {'content_type': 'Invalid content type.'}
            )
