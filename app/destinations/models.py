from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


from common import BaseModel


class Destination(BaseModel):
    name = models.CharField(max_length=150, unique=True, blank=False)


class Location(BaseModel):
    class LocationType(models.TextChoices):
        RESORT = "RE", _("resort")
        THEME_PARK = "TP", _("theme-park")
        WATER_PARK = "WP", _("water-park")
        ENTERTAINMENT_VENUE = "EV", _("entertainment-venue")

    name = models.CharField(max_length=200, blank=False, unique=True)
    location_type = models.CharField(
        max_length=2,
        choices=LocationType.choices,
        blank=False,
    )
    destination = models.ForeignKey(Destination, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return "{}:{}".format(self.name, self.get_location_type_display())


class Land(BaseModel):
    name = models.CharField(max_length=200, blank=False)
    park = models.ForeignKey(Location, blank=False, on_delete=models.CASCADE)


class Experience(BaseModel):
    class ExperienceType(models.TextChoices):
        ATTRACTION = "A", _("attraction")
        ENTERTAINMENT = "EN", _("entertainment")
        EVENT = "EV", _("event")
        RESTAURANT = "R", _("restaurant")
        DINING_EVENT = "DE", _("dining-event")
        DINNER_SHOW = "DS", _("dinner-show")

    name = models.CharField(max_length=150, unique=True, blank=False)
    land = models.ForeignKey(Land, blank=True, null=True, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, blank=False, on_delete=models.CASCADE)
    experience_type = models.CharField(
        max_length=2,
        choices=ExperienceType.choices,
        blank=False,
    )

    def __str__(self):
        return "{}:{}".format(self.name, self.get_experience_type_display())

    def clean(self):
        super().clean()
        # This method is used for object validation
        # Here we add our custom validation rule
        if self.land and self.location != self.land.park:
            raise ValidationError(
                "The land's park must match the experience's location"
            )


