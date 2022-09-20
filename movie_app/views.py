from uuid import uuid4
import uuid
from django.shortcuts import render, redirect
from django.views.generic import View, FormView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from .models import Movie, UserUniqueToken, User, Person
from .forms import UserRegisterForm, UserLoginForm, UserPasswordUpdateForm, UserPasswordResetForm, \
    UserPasswordSetForm, PersonForm
from .validators import validate_token

# Create your views here.


class TestMixin(UserPassesTestMixin):
    
    def test_func(self):

        return self.request.user.is_staff

    def handle_no_permission(self):
    
        messages.error(self.request, message='Twój profil nie posiada uprawnień.')
        
        return redirect(reverse_lazy('user-login'))


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
    Return user register form
    """
    form_class = UserRegisterForm
    template_name = 'movie_app/user_register.html'
    success_url = reverse_lazy('user-register')
   
    def form_valid(self, form):

        user = form.save()
        new_token = UserUniqueToken.objects.create(user=user)
        user.email_user(
            subject='Rejestracja konta',
            message=f'''Witaj {user}, twój link do aktywacji konta:
                {self.request.get_host()}{reverse_lazy('user-active-account')}?token={new_token.token}'''
        )
        messages.success(self.request, message='Profil został utworzony, sprawdź pocztę i kliknij w link aktywacyjny aby się zalogować')
        
        return super().form_valid(form)


class UserLoginView(FormView):

    """
    Return user login form
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
    Return user logout view
    """
    def get(self, request):

        if self.request.user.is_authenticated:

            logout(request)
        
        return redirect(reverse_lazy('index'))


class UserActiveAccountView(View):

    """
    Check user token and activ account
    """
    def get(self, request):

        token = request.GET.get('token')

        if token and validate_token(token) and UserUniqueToken.objects.filter(token=token).first():
            
            user_token = UserUniqueToken.objects.get(token=token)
            user = user_token.user
            user.is_active = True
            user.save()
            user_token.delete()
            messages.success(self.request, message='Profil został aktywowany.')
        
        else:
            messages.error(self.request, message='Twój link jest błędny lub źle podany !!! Spróbuj ponownie.')
        
        return redirect(reverse_lazy('user-login'))


class UserUpdateView(LoginRequiredMixin, UpdateView):
    
    """
    Return user update form
    """
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'avatar']
    template_name = 'movie_app/user_update.html'
    success_url = reverse_lazy('user-update')
    
    def get_object(self):
       
        return self.request.user

    def form_valid(self, form):
           
        form.save()
        messages.success(self.request, message='Zmieniono poprawnie twój profil')
        
        return super().form_valid(form)


class UserPasswordUpdateView(LoginRequiredMixin, UpdateView):
    
    """
    Return user password update form
    """
    model = User
    form_class = UserPasswordUpdateForm
    template_name = 'movie_app/user_password_update.html'
    success_url = reverse_lazy('user-login')
    
    def get_object(self):
       
        return self.request.user

    def form_valid(self, form):
        
        self.object.set_password(form.cleaned_data['password_new'])
        logout(self.request)
        messages.success(self.request, message='Zmieniono poprawnie twoje hasło, zaloguj się ponownie')
        
        return super().form_valid(form)


class UserPasswordResetView(FormView):

    """
    Return user password reset form
    """
    form_class = UserPasswordResetForm
    template_name = 'movie_app/user_password_reset.html'
    success_url = reverse_lazy('user-password-reset')
    
    def form_valid(self, form):

        user = User.objects.get(email=form.cleaned_data['email'])
        new_token, created = UserUniqueToken.objects.get_or_create(user=user)
        if user.is_active:
            user.email_user(
                subject='Resetowanie hasła',
                message=f'''Witaj {user}, twój link do ustawienia nowego hasła:
                    {self.request.get_host()}{reverse_lazy('user-password-set')}?token={new_token.token}'''
                )
            messages.success(self.request, message='Dziękujemy, sprawdź pocztę i kliknij w link resetujący hasło')
        else:
            user.email_user(
                subject='Aktywacja konta',
                message=f'''Witaj {user}, twój link do aktywacji konta:
                    {self.request.get_host()}{reverse_lazy('user-active-account')}?token={new_token.token}'''
                )
            messages.success(self.request, message='Profil nie został jeszcze aktywowany, sprawdź pocztę i kliknij w link aktywacyjny')
        
        return super().form_valid(form)


class UserPasswordSetView(UpdateView):
    
    """
    Return user password set form
    """
    model = User
    form_class = UserPasswordSetForm
    template_name = 'movie_app/user_password_set.html'
    success_url = reverse_lazy('user-login')
    
    def get_object(self):
       
        token = self.request.GET.get('token')
        
        if token and validate_token(token) and UserUniqueToken.objects.filter(token=token).first():
            self.user_token = UserUniqueToken.objects.get(token=token)
            return self.user_token.user

        else:
            messages.error(self.request, message='Twój link jest błędny lub źle podany !!! Spróbuj ponownie.')
     
    def form_valid(self, form):

        if self.object is None:
            
            return super().form_invalid(form)
        
        self.object.set_password(form.cleaned_data['password_new'])
        self.user_token.delete()
        messages.success(self.request, message='Zmieniono poprawnie twoje hasło, zaloguj się ponownie')
        
        return super().form_valid(form)


class PersonCreateView(TestMixin, CreateView):

    """
    Return person add view
    """
    model = Person
    form_class = PersonForm
    template_name = 'movie_app/person_form.html'

    def get_success_url(self):
    
        return reverse_lazy('person-detail', args=(self.object.pk,))
   
    def form_valid(self, form):
        
        self.object = form.save()
        messages.success(self.request, message='Dodano nowy profil')
                
        return super().form_valid(form)


class PersonUpdateView(LoginRequiredMixin, UpdateView):

    """
    Return the update person view
    """
    model = Person
    form_class = PersonForm
    template_name = 'movie_app/person_form.html'
    context_object_name = "person"
    
    def get_success_url(self):
    
        return reverse_lazy('person-detail', args=(self.object.pk,))
    

    def form_valid(self, form):
        
        self.object = form.save()
        messages.success(self.request, message='Profil został zmieniony')
                
        return super().form_valid(form)
