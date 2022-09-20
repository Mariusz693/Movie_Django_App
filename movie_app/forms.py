from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.contrib.auth import authenticate

from .models import User, Person
from .validators import validate_password


class DateInput(forms.DateInput):

    input_type = 'date'


class UserRegisterForm(forms.ModelForm):

    password = forms.CharField(label='Hasło', widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar', 'password', 'password_repeat']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)
        
        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']

        if password != password_repeat:
            self.add_error('password_repeat', 'Hasła róźnią się od siebie')

        try:
            validate_password(password=password)
        except ValidationError as e:
            self.add_error('password', e)
        
    def save(self, commit=True):

        return User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            avatar=self.cleaned_data['avatar'],
            password=self.cleaned_data['password'],
        )


class UserLoginForm(forms.Form):

    username = forms.CharField(label='Nazwa użytkownika', max_length=64)
    password = forms.CharField(label='Hasło', max_length=64, widget=forms.PasswordInput())

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.filter(username=username).first()
        
        if not user:
            self.add_error('username', 'Brak użytkownika o takiej nazwie')
        
        elif not authenticate(username=username, password=password):
            self.add_error('password', 'Błędne hasło')
    
    def authenticate_user(self):

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        
        user = authenticate(username=username, password=password)

        return user


class UserPasswordUpdateForm(forms.ModelForm):

    password_old = forms.CharField(label='Poprzednie hasło', widget=forms.PasswordInput())
    password_new = forms.CharField(label='Nowe hasło', widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['password_old', 'password_new', 'password_repeat']

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)
        
        password_old = self.cleaned_data['password_old']
        password_new = self.cleaned_data['password_new']
        password_repeat = self.cleaned_data['password_repeat']
        
        if not authenticate(username=self.instance.username, password=password_old):
            self.add_error('password_old', 'Błędne hasło')
    
        if password_new != password_repeat:
            self.add_error('password_repeat', 'Hasła róźnią się od siebie')

        try:
            validate_password(password=password_new)
        except ValidationError as e:
            self.add_error('password_new', e)


class UserPasswordResetForm(forms.Form):

    email = forms.CharField(label='Email', widget=forms.EmailInput())

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)

        email = self.cleaned_data['email']

        if not User.objects.filter(email=email).first():
            self.add_error('email', 'Brak użytkownika o podanym adresie email')


class UserPasswordSetForm(forms.ModelForm):

    password_new = forms.CharField(label='Nowe hasło', widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['password_new', 'password_repeat']

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)
        
        password_new = self.cleaned_data['password_new']
        password_repeat = self.cleaned_data['password_repeat']
        
        if password_new != password_repeat:
            self.add_error('password_repeat', 'Hasła róźnią się od siebie')

        try:
            validate_password(password=password_new)
        except ValidationError as e:
            self.add_error('password_new', e)


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'country', 'biography', 'avatar',]
        widgets = {
            'date_of_birth': DateInput(),
            'date_of_death': DateInput(),
            'biography': forms.Textarea(attrs={'rows':10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False

    def clean(self, *args, **kwargs):
        
        super().clean(*args, **kwargs)

        date_of_birth = self.cleaned_data['date_of_birth']
        date_of_death = self.cleaned_data['date_of_death']

        if date_of_death:
            if date_of_birth >= date_of_death:
                self.add_error('date_of_death', 'Data śmierci nie może być wcześniej niż urodzenia')
