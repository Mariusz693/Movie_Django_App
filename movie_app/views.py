from django.shortcuts import render, redirect
from django.views.generic import View, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout

from .models import Movie, UserUniqueToken
from .forms import UserRegisterForm, UserLoginForm

# Create your views here.


class IndexView(View):
    
    """
    Return Base View
    """
    def get(self, request):

        movies = Movie.objects.all()[:10]
        return render(
            request=request,
            template_name='movie_app/index.html',
            context={
                'movies': movies,
            }
        )


class UserRegisterView(FormView):

    """
    Return form to register user
    """
    form_class = UserRegisterForm
    template_name = 'movie_app/user_register.html'
    success_url = reverse_lazy('user-register')
   
    def form_valid(self, form):

        user = form.save()
        new_token = UserUniqueToken.objects.create(user=user)
        user.email_user(
            subject='Rejestracja konta',
            message=f'''Dziękujemy za rejestrację konta w naszym serwisie, twój link do aktywacji:
                {self.request.get_host()}{reverse_lazy('user-active-account')}?token={new_token.token}'''
        )
        messages.success(self.request, message='Profil został utworzony, sprawdź pocztę i kliknij w link aktywacyjny aby się zalogować')
        
        return super().form_valid(form)


class UserLoginView(FormView):

    """
    Return form to login user
    """
    form_class = UserLoginForm
    template_name = 'movie_app/user_login.html'

    def get_success_url(self):

        return self.request.GET.get('next') or reverse_lazy('index')

    def form_valid(self, form):

        user = form.authenticate_user()

        if user:
            login(self.request, user=user)

        return super().form_valid(form)


class UserLogoutView(View):

    """
    Logout user view
    """
    def get(self, request):

        if self.request.user.is_authenticated:

            logout(request)
        
        return redirect(reverse_lazy('index'))


class UserActiveAccountView(View):

    def get(self, request):

        token = request.GET.get('token')
        user_unique_token = UserUniqueToken.objects.filter(token=token).first()

        if user_unique_token:

            user = user_unique_token.user
            user.is_active = True
            user.save()
            messages.success(self.request, message='Profil został aktywowany.')
        
        else:
            messages.error(self.request, message='Twój link jest błędny lub źle podany !!! Spróbuj ponownie.')
        
        return redirect(reverse_lazy('login'))