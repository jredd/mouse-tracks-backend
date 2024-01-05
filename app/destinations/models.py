from django.db import models
from django.core.exceptions import ValidationError

from common import BaseModel


class Destination(BaseModel):
    name = models.CharField(max_length=150, unique=True, blank=False)
    disney_id = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        help_text="Unique identifier from Disney's API"
    )


class Location(BaseModel):
    class LocationType(models.TextChoices):
        RESORT = "resort"
        THEME_PARK = "theme-park"
        WATER_PARK = "water-park"
        ENTERTAINMENT_VENUE = "entertainment-venue"

    name = models.CharField(max_length=200, blank=False, unique=True)
    disney_id = models.CharField(max_length=150, unique=True, help_text="Unique identifier from Disney's API")
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        blank=False,
    )
    destination = models.ForeignKey(Destination, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return "{}:{}".format(self.name, self.get_location_type_display())


class Land(BaseModel):
    name = models.CharField(max_length=200, blank=False)
    disney_id = models.CharField(max_length=150, unique=True, help_text="Unique identifier from Disney's API")
    park = models.ForeignKey(Location, blank=False, on_delete=models.CASCADE)

    def clean(self):
        super().clean()

        if self.park.location_type not in [Location.LocationType.THEME_PARK, Location.LocationType.WATER_PARK]:
            raise ValidationError(
                "A land's park must be a theme park or a water park."
            )


class Experience(BaseModel):
    class ExperienceType(models.TextChoices):
        ATTRACTION = "attraction"
        ENTERTAINMENT = "entertainment"
        EVENT = "event"
        RESTAURANT = "restaurant"
        DINING_EVENT = "dining-event"
        DINNER_SHOW = "dinner-show"

    name = models.CharField(max_length=150, blank=False)
    short_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Shortened name for display purposes, especially on smaller screens.",
    )
    disney_id = models.CharField(max_length=150, unique=True, help_text="Unique identifier from Disney's API")
    lands = models.ManyToManyField(Land, blank=True)
    locations = models.ManyToManyField(Location, blank=True)
    destination = models.ForeignKey(Destination, blank=True, null=True, on_delete=models.PROTECT)
    experience_type = models.CharField(
        max_length=20,
        choices=ExperienceType.choices,
        blank=False,
    )

    def __str__(self):
        return "{}:{}".format(self.name, self.get_experience_type_display())

    def clean(self):
        super().clean()

        for land in self.lands.all():
            if land.park not in self.locations.all():
                raise ValidationError(
                    "Each land's park must be in the experience's locations"
                )

        if not self.locations.exists() and not self.destination:
            raise ValidationError(
                "The experience must be associated with at least one location or a destination."
            )
