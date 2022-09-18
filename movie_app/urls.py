from django.urls import path
from .views import IndexView, UserRegisterView, UserLoginView, UserLogoutView, UserActiveAccountView


urlpatterns = [
    path('', view=IndexView.as_view(), name='index'),
    path('user_register', view=UserRegisterView.as_view(), name='user-register'),
    path('user_login', view=UserLoginView.as_view(), name='user-login'),
    path('user_logout', view=UserLogoutView.as_view(), name='user-logout'),
    path('user_active_account', view=UserActiveAccountView.as_view()),
]