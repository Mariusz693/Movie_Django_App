from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import messages

from .models import User, Person, Movie, Genre, Character, Comment

# Register your models here.

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    ordering = ('username',)

    def delete_model(self, request, obj):

        superusers_count = User.objects.filter(is_superuser=True).count()
        user_status = 1 if obj.is_superuser else 0

        if superusers_count - user_status == 0:
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'Nie można usunąć ostatniego administratora !!!')

        else:
            obj.delete()

    def delete_queryset(self, request, queryset):

        superusers_count = User.objects.filter(is_superuser=True).count()
        superusers_in_queryset = queryset.filter(is_superuser=True).count()

        if superusers_count - superusers_in_queryset == 0:
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'Próbujesz usunąć wszystkich administratorów !!!')

        else:
            queryset.delete()


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'country')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'rating')

admin.site.register(Genre)

admin.site.register(Character)

admin.site.register(Comment)