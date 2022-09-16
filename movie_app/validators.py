from datetime import date
from django.core.exceptions import ValidationError


def validate_rating(rating):

    if rating < 1.0 or rating > 10.0:
        raise ValidationError("Wprowadź wartość w zakresie 1.0 - 10.0")


def validate_year(year):

    if year < 1900:
        raise ValidationError("Wprowadź wartość powyżej lub równą 1900")

    if year > date.today().year:
        raise ValidationError(f"Wprowadź wartość poniżej lub równą {date.today().year}")
