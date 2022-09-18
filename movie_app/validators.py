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


def validate_password(password):

    if len(password) < 7:
        raise ValidationError('Hasło za krótkie')

    contains_lower_char = False
    contains_upper_char = False
    
    for char in password:
        if char.islower():
            contains_lower_char = True
            break
    for char in password:
        if char.isupper():
            contains_upper_char = True
            break
    
    if (contains_lower_char is False) or (contains_upper_char is False):
        raise ValidationError('Hasło musi zawierać małe i duże litery')

    if not any([char.isdigit() for char in password]):
        raise ValidationError('Hasło musi zawierać minimum jedną cyfrę')

    special_char = """!@#$%^&*()_+-={}[]|\:";'<>?,./"""
    contains_special_char = False
    
    for char in special_char:
        if char in password:
            contains_special_char = True
            break
    
    if contains_special_char is False:
        raise ValidationError(f'Hasło musi zawierać znak specjalny {special_char}')