from django.urls import path
from .views import IndexView, UserRegisterView, UserLoginView, UserLogoutView, UserActiveAccountView, \
    UserUpdateView, UserPasswordUpdateView, UserPasswordResetView, UserPasswordSetView


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
]