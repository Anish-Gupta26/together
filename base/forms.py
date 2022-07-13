from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__' #Which all fields to be asked from user of model Room
        exclude = ['host','participants']

class UserForm(ModelForm):
    class Meta:
        model= User
        fields = ['avatar','name','username','email','bio']