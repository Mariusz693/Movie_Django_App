import uuid

from pathlib import Path

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser

from django_resized import ResizedImageField

# Create your models here.

def image_upload_handler(instance, filename):
    
    model_name = instance.__class__.__name__
    uuid_code = str(uuid.uuid1()).replace('-', '')[:8]
    file_suffix = Path(filename).suffix
    new_filename = f'{instance}_{uuid_code}'
    
    return f'movie_app/{model_name}/{new_filename}{file_suffix}'


class User(AbstractUser):

    class Meta:
            verbose_name = 'Użytkownik'
            verbose_name_plural = 'Użytkownicy'

    first_name = models.CharField(verbose_name='Imię', max_length=64)
    last_name = models.CharField(verbose_name='Nazwisko', max_length=64)
    is_active = models.BooleanField(verbose_name='Aktywny', default=False)
    username = models.CharField(
        verbose_name='Nazwa użytkownika',
        max_length=64,
        unique=True,
        error_messages={'unique': 'Nazwa użytkownika już zarejestrowana w serwisie'},
        )
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
        error_messages={'unique': 'Email już zarejestrowany w serwisie'},
        )
    avatar = ResizedImageField(
        size=[192, 256],
        crop=['middle', 'center'],
        force_format='PNG',
        upload_to=image_upload_handler,
        default='movie_app/default_person.png',
        verbose_name='Awatar'
        )
    
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):

        return self.username
    
    def email_user(self, subject, message, from_email='webmaster@localhost', *args, **kwargs):
        
        send_mail(subject, message, from_email, [self.email,], *args, **kwargs)
