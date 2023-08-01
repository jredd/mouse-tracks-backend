from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from common import BaseModel
from destinations import models as dest_models
from config.settings import AUTH_USER_MODEL

class Trip(BaseModel):
    title = models.CharField(max_length=150, blank=False)
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    destination = models.ForeignKey(dest_models.Destination, on_delete=models.CASCADE)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    def __str__(self):
        return f"{self.created_by.first_name}'s:{self.title}"


class Break(BaseModel):
    location = models.ForeignKey(dest_models.Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"Break: {self.location.name}"


class TravelEvent(BaseModel):
    class EventType(models.TextChoices):
        CHECK_IN = "CI", _("check-in")
        CHECK_OUT = "CO", _("check-out")
        PARK_HOP = "PH", _("park-hop")
        OTHER_TRAVEL = "OT", _("other-travel")

    from_location = models.ForeignKey(
        dest_models.Location, related_name='travels_from', blank=True, null=True, on_delete=models.SET_NULL
    )
    to_location = models.ForeignKey(
        dest_models.Location, related_name='travels_to', blank=True, null=True, on_delete=models.SET_NULL
    )
    custom_from_location = models.CharField(max_length=200, blank=True, null=True)
    custom_to_location = models.CharField(max_length=200, blank=True, null=True)
    travel_type = models.CharField(
        max_length=2,
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
        # Make sure that either from_location or custom_from_location is filled
        if not self.from_location and not self.custom_from_location:
            raise ValidationError({
                'from_location': 'Either from_location or custom_from_location must be filled.',
                'custom_from_location': 'Either from_location or custom_from_location must be filled.',
            })
        # Make sure that either to_location or custom_to_location is filled
        if not self.to_location and not self.custom_to_location:
            raise ValidationError({
                'to_location': 'Either to_location or custom_to_location must be filled.',
                'custom_to_location': 'Either to_location or custom_to_location must be filled.',
            })


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
        valid_content_types = ContentType.objects.get_for_models(dest_models.Experience, Break, TravelEvent)
        if self.content_type not in valid_content_types.values():
            raise ValidationError(
                {'content_type': 'Invalid content type.'}
            )
