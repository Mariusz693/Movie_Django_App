from django.urls import path
from .views import IndexView, UserRegisterView, UserLoginView, UserLogoutView, UserActiveAccountView, \
    UserUpdateView, UserPasswordUpdateView, UserPasswordResetView, UserPasswordSetView, PersonCreateView, \
        PersonUpdateView, PersonListView, PersonDetailView, PersonDeleteView, PersonMoviesListView


urlpatterns = [
    path('', view=IndexView.as_view(), name='index'),
    path('user_register', view=UserRegisterView.as_view(), name='user-register'),
    path('user_login', view=UserLoginView.as_view(), name='user-login'),
    path('user_logout', view=UserLogoutView.as_view(), name='user-logout'),
    path('user_active_account', view=UserActiveAccountView.as_view(), name='user-active-account'),
    path('user_update', view=UserUpdateView.as_view(), name='user-update'),
    path('user_password_update', view=UserPasswordUpdateView.as_view(), name='user-password-update'),
    path('user_password_reset', view=UserPasswordResetView.as_view(), name='user-password-reset'),
    path('user_password_set', view=UserPasswordSetView.as_view(), name='user-password-set'),
    path('person_list', view=PersonListView.as_view(), name='person-list'),
    path('person_create', view=PersonCreateView.as_view(), name='person-create'),
    path('person_update/<int:pk>', view=PersonUpdateView.as_view(), name='person-update'),
    path('person_detail/<int:pk>', view=PersonDetailView.as_view(), name='person-detail'),
    path('person_delete/<int:pk>', view=PersonDeleteView.as_view(), name='person-delete'),
    path('person_movies/<int:pk>/<str:status>', view=PersonMoviesListView.as_view(), name='person-movies'),
]