from django import forms
from user.models import User
from .models import Driver, Vehicle

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'phone_number', 'password']

class DriverRegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)
    vehicle_model = forms.CharField(max_length=255)
    vehicle_number = forms.CharField(max_length=20)

    class Meta:
        model = Driver
        fields = ['name', 'phone_number', 'password', 'vehicle_model', 'vehicle_number']

class VehicleRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['model', 'number']
