import uuid

from pathlib import Path

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser

from django_resized import ResizedImageField
from django_countries.fields import CountryField

from .validators import validate_year, validate_rating

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


class UserUniqueToken(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Person(models.Model):

    class Meta:
        verbose_name = 'Postać'
        verbose_name_plural = 'Postacie'
        unique_together = ['first_name', 'last_name']
        ordering = ['first_name', 'last_name']

    first_name = models.CharField(max_length=32, verbose_name='Imię')
    last_name = models.CharField(max_length=32, verbose_name='Nazwisko')
    date_of_birth = models.DateField(verbose_name='Data urodzenia')
    date_of_death = models.DateField(verbose_name='Data śmierci', null=True, blank=True)
    biography = models.TextField(verbose_name='Biografia', blank=True)
    country = CountryField(blank_label='Wybierz z listy', verbose_name='Kraj pochodzenia')
    liked_by = models.ManyToManyField(
        'User',
        related_name='liked_persons',
        verbose_name='Polubienia',
        blank=True
        )
    avatar = ResizedImageField(
        size=[192, 256],
        crop=['middle', 'center'],
        force_format='PNG',
        upload_to=image_upload_handler,
        default='movie_app/default_person.png',
        verbose_name='Awatar'
        )
    
    def __str__(self):

        return self.first_name + ' ' + self.last_name

    def unique_error_message(self, model_class, unique_check):

        if unique_check == ('first_name', 'last_name'):
            return 'Postać już zapisana w serwisie'

        return super().unique_error_message(model_class, unique_check)


class Genre(models.Model):

    class Meta:
        verbose_name = 'Gatunek'
        verbose_name_plural = 'Gatunki'
        ordering = ['name']

    name = models.CharField(
        max_length=32,
        unique=True,
        error_messages={'unique':'Nazwa gatunku już zapisana w serwisie'},
        verbose_name='Nazwa'
        )
    
    def __str__(self):
        
        return self.name


class Movie(models.Model):

    class Meta:
        verbose_name = 'Film'
        verbose_name_plural = 'Filmy'
        ordering = ['-rating', 'title']

    title = models.CharField(max_length=128, verbose_name='Tytuł')
    duration = models.DurationField(verbose_name='Czas trwania')
    plot = models.TextField(verbose_name='Fabuła', blank=True)
    year = models.PositiveSmallIntegerField(verbose_name='Rok produkcji', validators=[validate_year])
    rating = models.DecimalField(verbose_name='Ranking', max_digits=3, decimal_places=1, validators=[validate_rating])
    director = models.ForeignKey(
        'Person',
        related_name='directors',
        verbose_name='Reżyseria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )
    screenplay = models.ForeignKey(
        'Person',
        related_name='screenplays',
        verbose_name='Scenariusz',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )
    characters = models.ManyToManyField(
        'Person',
        related_name='starrings',
        verbose_name='Aktorzy',
        through='Character',
        blank=True
        )
    comments = models.ManyToManyField(
        'User',
        related_name='comment_movies',
        verbose_name='Komentarze',
        through='Comment',
        blank=True
        )
    liked_by = models.ManyToManyField(
        'User',
        related_name='liked_movies',
        verbose_name='Polubienia',
        blank=True
        )
    genre = models.ManyToManyField(
        'Genre',
        related_name='genries',
        verbose_name='Gatunek',
        blank=True
        )
    avatar = ResizedImageField(
        size=[192, 256],
        crop=['middle', 'center'],
        force_format='PNG',
        upload_to=image_upload_handler,
        default='movie_app/default_movie.png',
        verbose_name='Awatar'
        )
    
    def __str__(self):
        
        return self.title


class Character(models.Model):

    class Meta:
        verbose_name = 'Postać w filmie'
        verbose_name_plural = 'Postacie w filmach'
        unique_together = ['person', 'movie']
        ordering = ['movie']
        
    role = models.CharField(max_length=128, verbose_name='Postac')
    person = models.ForeignKey(
        'Person',
        related_name='person_characters',
        verbose_name='Aktor',
        on_delete=models.CASCADE
        )
    movie = models.ForeignKey(
        'Movie',
        related_name='movie_characters',
        verbose_name='Film',
        on_delete=models.CASCADE
        )
    
    def __str__(self):

        return f'{self.person}, {self.movie}, {self.role}'
    
    def unique_error_message(self, model_class, unique_check):

        if unique_check == ('person', 'movie'):
            return f'Aktor już ma przypisaną rolę w tym filmie'

        return super().unique_error_message(model_class, unique_check)


class Comment(models.Model):

    class Meta:
        verbose_name = 'Komentarz'
        verbose_name_plural = 'Komentarze'
        unique_together = ['movie', 'user']
        ordering = ['movie']
        
    comment = models.TextField(verbose_name='Komentarz')
    movie = models.ForeignKey(
        'Movie',
        related_name='movie_comments',
        verbose_name='Film',
        on_delete=models.CASCADE
        )
    user = models.ForeignKey(
        'User',
        related_name='user_comments',
        verbose_name='Użytkownik',
        on_delete=models.CASCADE
        )

    def __str__(self):

        return f'{self.movie}, {self.user}'
    
    def unique_error_message(self, model_class, unique_check):

        if unique_check == ('movie', 'user'):
            return f'Użytkownik już skomentował ten film'

        return super().unique_error_message(model_class, unique_check)