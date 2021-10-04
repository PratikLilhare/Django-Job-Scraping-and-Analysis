from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth import logout

def about(request):
    return render(request, 'about.html')


def get_started(request):
    return render(request, 'getStarted.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username= username, password= password)
        if user is not None:
            login(request, user)

            return redirect('/jobs/')

    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        user = User.objects.create_user(username, email, password)
        if user is not None:
            user.save()

            return redirect('/login/')
    

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    
    return render(request, "homepage.html")

def home(request):
    return render(request, "homepage.html")