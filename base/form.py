from django import forms
from .models import Room, Topic, User
from django.contrib.auth.forms import UserCreationForm

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'description']
    
    topic = forms.CharField(max_length=200)
    
    def save(self, commit=True, host=None):
        topic_name = self.cleaned_data['topic'].strip()
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = super().save(commit=False)
        room.topic = topic
        if host:
            room.host = host
        if commit:
            room.save()
        return room


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def clean_username(self): # form.is_valid حول الإسم الى حروف صغيرة قبل ارسالها الى clean اثناء عملية ال
        username = self.cleaned_data['username'].strip().lower()
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        return email


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']

    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        return email.strip().lower()