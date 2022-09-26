from django.urls import path

from .views import IndexView, ConfirmationView, UserRegisterView, UserLoginView, UserLogoutView, UserActiveAccountView, \
    UserUpdateView, UserPasswordUpdateView, UserPasswordResetView, UserPasswordSetView, UserDeleteView, UserMoviesView, GenreCreateView, \
        GenreUpdateView, GenreDeleteView, GenreListView, PersonCreateView, PersonUpdateView, PersonDeleteView, \
            PersonDetailView, PersonMoviesView, PersonListView, MovieCreateView, MovieUpdateView, MovieDeleteView, \
                MovieDetailView, MoviePersonsView, MovieListView, ContactView, UserMovieView, UserPersonsView, UserPersonView
                


urlpatterns = [
    path('', view=IndexView.as_view(), name='index'),
    path('confirmation', view=ConfirmationView.as_view(), name='confirmation'),
    path('user_register', view=UserRegisterView.as_view(), name='user-register'),
    path('user_login', view=UserLoginView.as_view(), name='user-login'),
    path('user_logout', view=UserLogoutView.as_view(), name='user-logout'),
    path('user_active_account', view=UserActiveAccountView.as_view(), name='user-active-account'),
    path('user_update', view=UserUpdateView.as_view(), name='user-update'),
    path('user_password_update', view=UserPasswordUpdateView.as_view(), name='user-password-update'),
    path('user_password_reset', view=UserPasswordResetView.as_view(), name='user-password-reset'),
    path('user_password_set', view=UserPasswordSetView.as_view(), name='user-password-set'),
    path('user_delete', view=UserDeleteView.as_view(), name='user-delete'),
    path('user_movie/<int:pk>', view=UserMovieView.as_view(), name='user-movie'),
    path('user_movies', view=UserMoviesView.as_view(), name='user-movies'),
    path('user_person/<int:pk>', view=UserPersonView.as_view(), name='user-person'),
    path('user_persons', view=UserPersonsView.as_view(), name='user-persons'),
    path('genre_create', view=GenreCreateView.as_view(), name='genre-create'),
    path('genre_update/<int:pk>', view=GenreUpdateView.as_view(), name='genre-update'),
    path('genre_delete/<int:pk>', view=GenreDeleteView.as_view(), name='genre-delete'),
    path('genre_list', view=GenreListView.as_view(), name='genre-list'),
    path('person_create', view=PersonCreateView.as_view(), name='person-create'),
    path('person_update/<int:pk>', view=PersonUpdateView.as_view(), name='person-update'),
    path('person_delete/<int:pk>', view=PersonDeleteView.as_view(), name='person-delete'),
    path('person_detail/<int:pk>', view=PersonDetailView.as_view(), name='person-detail'),
    path('person_movies/<int:pk>/<str:status>', view=PersonMoviesView.as_view(), name='person-movies'),
    path('person_list', view=PersonListView.as_view(), name='person-list'),
    path('movie_create/', MovieCreateView.as_view(), name='movie-create'),
    path('movie_update/<int:pk>', view=MovieUpdateView.as_view(), name='movie-update'),
    path('movie_delete/<int:pk>', view=MovieDeleteView.as_view(), name='movie-delete'),
    path('movie_detail/<int:pk>', view=MovieDetailView.as_view(), name='movie-detail'),
    path('movie_persons/<int:pk>', view=MoviePersonsView.as_view(), name='movie-persons'),
    path('movie_list', view=MovieListView.as_view(), name='movie-list'),
    path('contact', view=ContactView.as_view(), name='contact'),
]