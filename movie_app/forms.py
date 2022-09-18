from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate


from .models import User
from .validators import validate_password


class UserRegisterForm(forms.ModelForm):

    password = forms.CharField(label='Hasło', widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar', 'password', 'password_repeat']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False

    def clean(self):

        super().clean()
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']

        if User.objects.filter(username=username).first():
            self.add_error('username', 'Nazwa użytkownika już zarejestrowana w serwisie')
        
        if User.objects.filter(email=email).first():
            self.add_error('email', 'Email już zarejestrowany w serwisie')
        
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