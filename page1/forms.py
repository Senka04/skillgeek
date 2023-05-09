from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Video, TutorProfile, UserProfile
from django.core.exceptions import ValidationError


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'file', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-lg btn-primary'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-lg btn-primary'}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'file': 'Видео',
            'image': 'Обложка',
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=30, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    patronymic = forms.CharField(max_length=30, required=False)
    is_tutor = forms.BooleanField(required=False)
    discipline = forms.CharField(max_length=50, required=False)
    hourly_rate = forms.DecimalField(max_digits=6, decimal_places=2, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'patronymic', 'is_tutor',
                  'discipline', 'hourly_rate']

    def clean(self):
        cleaned_data = super().clean()
        self.errors.clear()
        # check the last_name, first_name, email, username, password1, password2 fields
        last_name = cleaned_data.get('last_name')
        if not last_name:
            self.add_error('last_name', 'Пожалуйста, введите фамилию.')

        first_name = cleaned_data.get('first_name')
        if not first_name:
            self.add_error('first_name', 'Пожалуйста, введите имя.')

        username = cleaned_data.get('username')
        if not username:
            self.add_error('username', 'Пожалуйста, введите никнейм.')
        elif UserProfile.objects.filter(username=username).exists() or TutorProfile.objects.filter(
                username=username).exists():
            self.add_error('username', 'Пользователь с таким никнеймом уже существует.')

        email = cleaned_data.get('email')
        if not email:
            self.add_error('email', 'Пожалуйста, введите электронную почту.')
        elif UserProfile.objects.filter(email=email.lower()).exists() or TutorProfile.objects.filter(email=email.lower()).exists():
            self.add_error('email', 'Эта электронная почта уже используется.')

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password1:
            self.add_error('password1', 'Пожалуйста, введите пароль.')
        elif not password2:
            self.add_error('password2', 'Пароли не совпадают.')

        return cleaned_data
    def save(self, commit=True):
        user = super().save(commit=True)
        user.set_password(self.cleaned_data['password1'])
        if self.cleaned_data['is_tutor']:
            tutor_profile = TutorProfile.objects.create(
                user=user,
                discipline=self.cleaned_data['discipline'].lower(),
                hourly_rate=self.cleaned_data['hourly_rate'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                patronymic=self.cleaned_data['patronymic'],
                email=self.cleaned_data['email'].lower(),
                username=self.cleaned_data['username']
            )
            tutor_profile.save()
        else:
            user_profile = UserProfile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                patronymic=self.cleaned_data['patronymic'],
                email=self.cleaned_data['email'].lower(),
                username=self.cleaned_data['username']
            )
            user_profile.save()

        if commit:
            user.save()

        return user
