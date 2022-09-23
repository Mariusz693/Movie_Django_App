from uuid import uuid4
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, FormView, UpdateView, CreateView, ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from .models import Movie, UserUniqueToken, User, Person, Genre
from .forms import UserRegisterForm, UserLoginForm, UserPasswordUpdateForm, UserPasswordResetForm, \
    UserPasswordSetForm, PersonForm, PersonSearchForm
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


class PersonUpdateView(TestMixin, UpdateView):

    """
    Return the update person view
    """
    model = Person
    form_class = PersonForm
    template_name = 'movie_app/person_form.html'
    context_object_name = "person"
    
    def get_success_url(self):
    
        return reverse_lazy('person-detail', args=(self.object.pk,))
    

class PersonDeleteView(TestMixin, DeleteView):

    """
    Return the delete person view
    """
    model = Person
    template_name = 'movie_app/person_delete.html'
    context_object_name = 'person'
    success_url = reverse_lazy('person-list')


class PersonDetailView(DetailView):

    """
    Return the detail person view
    """
    model = Person
    template_name = 'movie_app/person_detail.html'
    context_object_name = 'person'
    
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        if self.object.date_of_death is None:
            age = date.today().year - self.object.date_of_birth.year
            context['age'] = age

        return context


class PersonListView(ListView):

    """
    Return the person list view
    """
    model = Person
    template_name = 'movie_app/person_list.html'
    context_object_name = 'person_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):

        person_list = Person.objects.all()
        self.form = PersonSearchForm(self.request.GET)
        self.search_count = ''
        
        if self.form.is_valid():
            
            if 'first_name' in self.form.changed_data:
                person_list = person_list.filter(first_name__icontains=self.form.cleaned_data['first_name'])
            
            if 'last_name' in self.form.changed_data:
                person_list = person_list.filter(last_name__icontains=self.form.cleaned_data['last_name'])
            
            if self.form.changed_data:
                self.search_count = person_list.count()
                
        return person_list
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['form'] = self.form
        context['search_count'] = self.search_count
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context


class PersonMoviesListView(ListView):

    """
    Return the list all movie for person view
    """
    template_name = 'movie_app/person_movies.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        
        self.person = get_object_or_404(Person, pk=self.kwargs['pk'])
        self.status = self.kwargs['status']

        if self.status == 'director':

            return self.person.directors.all()
        
        elif self.status == 'screenplay':

            return self.person.screenplays.all()
        
        elif self.status != 'character':
            self.status = 'character'

        return self.person.person_characters.all()
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        context['person'] = self.person
        context['status'] = self.status

        return context


class GenreListView(TestMixin, ListView):

    """
    Return the genre list view
    """
    model = Genre
    template_name = 'movie_app/genre_list.html'
    context_object_name = 'genre_list'


class GenreCreateView(TestMixin, CreateView):

    """
    Return the add genre view
    """
    model = Genre
    fields = ['name']
    template_name = 'movie_app/genre_form.html'
    success_url = reverse_lazy('genre-list')


class GenreUpdateView(TestMixin, UpdateView):

    """
    Return the edit genre view
    """
    model = Genre
    fields = ['name']
    template_name = 'movie_app/genre_form.html'
    context_object_name = 'genre'
    success_url = reverse_lazy('genre-list')


class GenreDeleteView(TestMixin, DeleteView):

    """
    Return the delete genre view
    """
    model = Genre
    template_name = 'movie_app/genre_delete.html'
    context_object_name = 'genre'
    success_url = reverse_lazy('genre-list')
