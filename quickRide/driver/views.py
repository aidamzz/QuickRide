from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, DriverRegistrationForm, VehicleRegistrationForm
from .models import Driver, Vehicle
from user.models import User

class DriverRegistrationView(View):
    def get(self, request):
        form = DriverRegistrationForm()
        return render(request, 'driver/register_driver.html', {'form': form})

    def post(self, request):
        form = DriverRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create(
                name=form.cleaned_data['name'],
                phone_number=form.cleaned_data['phone_number']
            )
            user.set_password(form.cleaned_data['password'])
            user.save()

            driver = Driver.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number']
            )

            vehicle = Vehicle.objects.create(
                driver=driver,
                model=form.cleaned_data['vehicle_model'],
                number=form.cleaned_data['vehicle_number']
            )

            login(request, user)
            return redirect('home')
        return render(request, 'driver/register_driver.html', {'form': form})

def register_vehicle(request):
    if request.method == 'POST':
        form = VehicleRegistrationForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.driver = Driver.objects.get(user=request.user)
            vehicle.save()
            return redirect('home')
    else:
        form = VehicleRegistrationForm()
    return render(request, 'driver/register_vehicle.html', {'form': form})

class DriverLoginView(View):
    def get(self, request):
        return render(request, 'driver/login_driver.html')

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password')
            user = authenticate(phone_number=phone_number, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
        return render(request, 'driver/login_driver.html', {'form': form})
