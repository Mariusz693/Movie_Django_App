import os
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, FormView, UpdateView, CreateView, ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from formtools.wizard.views import SessionWizardView
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import NON_FIELD_ERRORS


from .models import Movie, UserUniqueToken, User, Person, Genre, Comment
from .forms import UserRegisterForm, UserLoginForm, UserPasswordUpdateForm, UserPasswordResetForm, \
    UserPasswordSetForm, CommentForm, PersonForm, PersonSearchForm, MovieFormStep1, MovieFormStep2, \
        MovieFormStep3, MovieFormsetStep4, MovieSearchForm, ContactForm
from .validators import validate_token

# Create your views here.


FORMS_MOVIE = [
    ('step1', MovieFormStep1),
    ('step2', MovieFormStep2),
    ('step3', MovieFormStep3),
    ('step4', MovieFormsetStep4)
]

TEMPLATES_MOVIE = {
    'step1': 'movie_app/movie_form_step1.html',
    'step2': 'movie_app/movie_form_step2.html',
    'step3': 'movie_app/movie_form_step3.html',
    'step4': 'movie_app/movie_formset_step4.html',
}


class TestMixin(UserPassesTestMixin):
    
    def test_func(self):

        return self.request.user.is_staff

    def handle_no_permission(self):

        if self.request.user.is_authenticated:
            
            messages.error(self.request, message='Twoje konto nie posiada uprawnień.')
        
            return redirect(reverse_lazy('confirmation'))
        
        return redirect(reverse_lazy('user-login')+f'?next={self.request.get_full_path()}')


class IndexView(View):
    
    """
    Return Base View
    """
    def get(self, request, *args, **kwargs):

        movies = Movie.objects.all()[:10]
        return render(
            request=request,
            template_name='movie_app/index.html',
            context={
                'movies': movies,
            }
        )


class ConfirmationView(View):

    """
    Return confirmation view
    """
    def get(self, request, *args, **kwargs):

        return render(
            request=request,
            template_name='movie_app/confirmation.html',
        )


class UserRegisterView(FormView):

    """
    Return user register form
    """
    form_class = UserRegisterForm
    template_name = 'movie_app/user_register.html'
    success_url = reverse_lazy('confirmation')
   
    def form_valid(self, form, *args, **kwargs):

        user = form.save()
        new_token = UserUniqueToken.objects.create(user=user)
        user.email_user(
            subject='Rejestracja konta',
            message=f'''Witaj {user}, twój link do aktywacji konta:
                {self.request.get_host()}{reverse_lazy('user-active-account')}?token={new_token.token}'''
        )
        messages.success(self.request, message='Konto zostało utworzone, sprawdź pocztę i kliknij w link aktywacyjny aby się zalogować')
        
        return super().form_valid(form, *args, **kwargs)


class UserLoginView(FormView):

    """
    Return user login form
    """
    form_class = UserLoginForm
    template_name = 'movie_app/user_login.html'

    def get_success_url(self, *args, **kwargs):

        return self.request.GET.get('next') or reverse_lazy('index')

    def form_valid(self, form, *args, **kwargs):

        user = form.authenticate_user()

        if user:
            login(self.request, user=user)

        return super().form_valid(form, *args, **kwargs)


class UserLogoutView(View):

    """
    Return user logout view
    """
    def get(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:

            logout(request)
        
        return redirect(reverse_lazy('index'))


class UserActiveAccountView(View):

    """
    Check user token and activ account
    """
    def get(self, request, *args, **kwargs):

        token = request.GET.get('token')

        if token and validate_token(token) and UserUniqueToken.objects.filter(token=token).first():
            
            user_token = UserUniqueToken.objects.get(token=token)
            user = user_token.user
            user.is_active = True
            user.save()
            user_token.delete()
            
            return redirect(reverse_lazy('user-login'))
        
        else:
            messages.error(self.request, message='Twój link jest błędny lub źle podany !!! Spróbuj ponownie.')

            return redirect(reverse_lazy('confirmation'))


class UserUpdateView(LoginRequiredMixin, UpdateView):
    
    """
    Return user update form
    """
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'avatar']
    template_name = 'movie_app/user_update.html'
    success_url = reverse_lazy('index')
    
    def get_object(self, *args, **kwargs):
       
        return self.request.user


class UserPasswordUpdateView(LoginRequiredMixin, UpdateView):
    
    """
    Return user password update form
    """
    model = User
    form_class = UserPasswordUpdateForm
    template_name = 'movie_app/user_password_update.html'
    success_url = reverse_lazy('user-login')
    
    def get_object(self, *args, **kwargs):
       
        return self.request.user

    def form_valid(self, form, *args, **kwargs):
        
        self.object.set_password(form.cleaned_data['password_new'])
        logout(self.request)
        
        return super().form_valid(form, *args, **kwargs)


class UserPasswordResetView(FormView):

    """
    Return user password reset form
    """
    form_class = UserPasswordResetForm
    template_name = 'movie_app/user_password_reset.html'
    success_url = reverse_lazy('confirmation')
    
    def form_valid(self, form, *args, **kwargs):

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
            messages.success(self.request, message='Konto nie zostało jeszcze aktywowany, sprawdź pocztę i kliknij w link aktywacyjny')
        
        return super().form_valid(form, *args, **kwargs)


class UserPasswordSetView(View):
    
    """
    Return user password set form
    """    
    def get(self, request, *args, **kwargs):
       
        token = request.GET.get('token')
        
        if token and validate_token(token) and UserUniqueToken.objects.filter(token=token).first():

            return render(
                request=request,
                template_name='movie_app/user_password_set.html',
                context={
                    'form': UserPasswordSetForm,
                }
            )

        else:
            messages.error(self.request, message='Twój link jest błędny lub źle podany !!! Spróbuj ponownie.')
            
            return redirect(reverse_lazy('confirmation'))
     
    def post(self, request, *args, **kwargs):
        
        form = UserPasswordSetForm(request.POST)

        if form.is_valid():
            token = request.GET.get('token')
            user_unique_token = UserUniqueToken.objects.filter(token=token).first()
            password_new = form.cleaned_data['password_new']
            user = user_unique_token.user
            user.set_password(password_new)
            user.save()
            user_unique_token.delete()

            return redirect('user-login')


class UserDeleteView(LoginRequiredMixin, DeleteView):

    """
    Return the delete user view
    """
    model = User
    template_name = 'movie_app/user_delete.html'
    success_url = reverse_lazy('confirmation')

    def get_object(self, *args, **kwargs):
       
        return self.request.user

    def form_valid(self, form, *args, **kwargs):

        staff_count = User.objects.filter(is_superuser=False, is_staff=True).count()
        user_status = 1 if self.object.is_staff else 0

        if staff_count - user_status == 0:
            form.add_error(NON_FIELD_ERRORS, "Jesteś ostatnim użytkownikiem z załogi, nie możesz usunąć konta")
        
            return self.form_invalid(form, *args, **kwargs)
        
        messages.success(self.request, message='Konto zostało usunięte')
           
        return super().form_valid(form, *args, **kwargs)


class UserMoviesView(LoginRequiredMixin, ListView):

    """
    Return the list all liked movies by user
    """
    model = Movie
    template_name = 'movie_app/user_movies.html'
    context_object_name = 'movie_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):

        return self.request.user.liked_movies.all()


class UserMovieView(LoginRequiredMixin, View):

    """
    Add or remove relation user with movie
    """
    def get(self, request, pk, *args, **kwargs):
        
        user = request.user
        movie = get_object_or_404(Movie, pk=pk)
        next = request.GET.get('next')
        
        if user in movie.liked_by.all():
            movie.liked_by.remove(user)
            
        else:
            movie.liked_by.add(user)
            
        return redirect(next)


class UserPersonsView(LoginRequiredMixin, ListView):

    """
    Return the list all liked persons by user
    """
    model = Person
    template_name = 'movie_app/user_persons.html'
    context_object_name = 'person_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):

        return self.request.user.liked_persons.all()


class UserPersonView(LoginRequiredMixin, View):

    """
    Add or remove relation user with person
    """
    def get(self, request, pk, *args, **kwargs):
        
        user = request.user
        person = get_object_or_404(Person, pk=pk)
        next = request.GET.get('next')
        
        if user in person.liked_by.all():
            person.liked_by.remove(user)
            
        else:
            person.liked_by.add(user)
            
        return redirect(next)


class UserCommentsView(LoginRequiredMixin, ListView):

    """
    Return the list all comments movie by user
    """
    model = Comment
    template_name = 'movie_app/user_comments.html'
    context_object_name = 'comment_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):

        return self.request.user.user_comments.all()


class UserCommentDeleteView(LoginRequiredMixin, View):

    """
    Remove user comment for movie
    """
    def get(self, request, pk, *args, **kwargs):
        
        comment = get_object_or_404(Comment, pk=pk)
        next = request.GET.get('next')
        comment.delete()
            
        return redirect(next)


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


class GenreListView(TestMixin, ListView):

    """
    Return the genre list view
    """
    model = Genre
    template_name = 'movie_app/genre_list.html'
    context_object_name = 'genre_list'


class PersonCreateView(TestMixin, CreateView):

    """
    Return person add view
    """
    model = Person
    form_class = PersonForm
    template_name = 'movie_app/person_form.html'

    def get_success_url(self, *args, **kwargs):
    
        return reverse_lazy('person-detail', args=(self.object.pk,))


class PersonUpdateView(TestMixin, UpdateView):

    """
    Return the update person view
    """
    model = Person
    form_class = PersonForm
    template_name = 'movie_app/person_form.html'
    context_object_name = "person"
    
    def get_success_url(self, *args, **kwargs):
    
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


class PersonMoviesView(DetailView):

    """
    Return the detail person view for list all movies
    """
    model = Person
    template_name = 'movie_app/person_movies.html'
    context_object_name = 'person'
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        context['status'] = self.kwargs['status']

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


class MovieCreateView(TestMixin, SessionWizardView):

    """
    Return the create movie view in four step
    """
    instance = None
    form_list = FORMS_MOVIE
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, ''))

    def get_form_instance(self, step, *args, **kwargs):
        
        if self.instance is None:
            self.instance = Movie() 
        
        return self.instance

    def get_template_names(self, *args, **kwargs):
        
        return [TEMPLATES_MOVIE[self.steps.current]]
    
    def done(self, form_list, *args, **kwargs):
        
        self.instance.save()
        self.instance.genre.set(form_list[2].cleaned_data['genre'])
        formset = form_list[3]
        formset.instance = self.instance
        formset.save()
        
        return redirect(reverse_lazy('movie-detail', args=(self.instance.pk,)))


class MovieUpdateView(TestMixin, SessionWizardView):

    """
    Return the update movie view in four step
    """
    instance = None
    form_list = FORMS_MOVIE
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, ''))
    
    def get_form_instance(self, step, *args, **kwargs):
        
        self.movie = get_object_or_404(Movie, pk=self.kwargs['pk'])
        
        if self.instance is None:
            self.instance = self.movie
        
        return self.instance

    def get_template_names(self, *args, **kwargs):
        
        return [TEMPLATES_MOVIE[self.steps.current]]
    
    def get_context_data(self, form, *args, **kwargs):
        
        context = super().get_context_data(form, *args, **kwargs)
        context['movie'] = self.movie
        
        return context
    
    def done(self, form_list, *args, **kwargs):
        
        self.instance.save()
        self.instance.genre.set(form_list[2].cleaned_data['genre'])
        formset = form_list[3]
        formset.save()
        
        messages.success(self.request, message='Film został zmieniony')
        
        return redirect(reverse_lazy('movie-detail', args=(self.instance.pk,)))


class MovieDeleteView(TestMixin, DeleteView):

    """
    Return the delete movie view
    """
    model = Movie
    template_name = 'movie_app/movie_delete.html'
    context_object_name = 'movie'
    success_url = reverse_lazy('movie-list')


class MovieDetailView(DetailView):

    """
    Return the detail movie view
    """
    model = Movie
    template_name = 'movie_app/movie_detail.html'
    context_object_name = 'movie'

    def post(self, *args, **kwargs):
        form = CommentForm(self.request.POST)
        if form.is_valid():
            form.save()

        return redirect(reverse_lazy('movie-detail', args=(self.get_object().pk,)) + f'#comments')

    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        if self.request.user.is_authenticated and not self.request.user in self.object.comments.all():
            form = CommentForm()
            form.initial['user'] = self.request.user
            form.initial['movie'] = self.object
            context['form'] = form
        
        return context


class MoviePersonsView(DetailView):

    """
    Return the detail movie view for list all persons
    """
    model = Movie
    template_name = 'movie_app/movie_persons.html'
    context_object_name = 'movie'
    

class MovieCommentsView(DetailView):

    """
    Return the detail movie view for list all comments
    """
    model = Movie
    template_name = 'movie_app/movie_comments.html'
    context_object_name = 'movie'


class MovieListView(ListView):

    """
    Return the movie list view
    """
    model = Movie
    template_name = 'movie_app/movie_list.html'
    context_object_name = 'movie_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):

        movie_list = Movie.objects.all()
        self.form = MovieSearchForm(self.request.GET)
        self.search_count = ''
        
        if self.form.is_valid():
            
            if 'title' in self.form.changed_data:
                movie_list = movie_list.filter(title__icontains=self.form.cleaned_data['title'])
            if 'director' in self.form.changed_data:
                movie_list = movie_list.filter(director=self.form.cleaned_data['director'])
            if 'screenplay' in self.form.changed_data:
                movie_list = movie_list.filter(screenplay=self.form.cleaned_data['screenplay'])
            if 'character' in self.form.changed_data:
                movie_list = movie_list.filter(characters=self.form.cleaned_data['character'])
            if 'year_from' in self.form.changed_data:
                movie_list = movie_list.filter(year__gte=self.form.cleaned_data['year_from'])
            if 'year_to' in self.form.changed_data:
                movie_list = movie_list.filter(year__lte=self.form.cleaned_data['year_to'])
            if 'rating_from' in self.form.changed_data:
                movie_list = movie_list.filter(rating__gte=self.form.cleaned_data['rating_from'])
            if 'rating_to' in self.form.changed_data:
                movie_list = movie_list.filter(rating__lte=self.form.cleaned_data['rating_to'])
            if 'genre' in self.form.changed_data:
                for genre in self.form.cleaned_data['genre']:
                    movie_list = movie_list.filter(genre=genre)

            if self.form.changed_data:
                self.search_count = movie_list.count()
             
        return movie_list
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['form'] = self.form
        context['search_count'] = self.search_count
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context


class ContactView(FormView):

    """
    Return contact form
    """
    form_class = ContactForm
    template_name = 'movie_app/contact_form.html'
    success_url = reverse_lazy('confirmation')
   
    def form_valid(self, form, *args, **kwargs):

        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        staff_users = User.objects.filter(is_staff=True)
        for user in staff_users:
            user.email_user(
                subject=subject,
                message=f'{first_name} {last_name} : {message}',
                from_email=email
            )
        messages.success(self.request, message='Twoja wiadomość została wysłana')
        
        return super().form_valid(form, *args, **kwargs)