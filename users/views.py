# Shivoham Mishra | BTech

from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib import messages


def login_page(request):

    if request.method == 'POST':

        action = request.POST.get('action')



        # =====================================
        # LOGIN
        # =====================================

        if action == 'login':

            username = request.POST.get('username')

            password = request.POST.get('password')

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                return redirect('/')

            else:

                messages.error(
                    request,
                    'Invalid Username or Password'
                )

                return redirect('/login/')



        # =====================================
        # REGISTER
        # =====================================

        elif action == 'register':

            username = request.POST.get('username')

            email = request.POST.get('email')

            password = request.POST.get('password')



            # USERNAME CHECK

            if User.objects.filter(username=username).exists():

                messages.error(
                    request,
                    'Username Already Exists'
                )

                return redirect('/login/')



            # EMAIL CHECK

            if User.objects.filter(email=email).exists():

                messages.error(
                    request,
                    'Email Already Registered'
                )

                return redirect('/login/')



            # CREATE USER

            User.objects.create_user(

                username=username,

                email=email,

                password=password
            )



            messages.success(
                request,
                'Account Created Successfully'
            )

            return redirect('/login/')



    return render(
        request,
        'login.html'
    )




def home(request):

    return render(
        request,
        'home.html'
    )




def services_page(request):

    return render(
        request,
        'services.html'
    )




def events_page(request):

    return render(
        request,
        'events.html'
    )
from django.contrib.auth import logout


def logout_page(request):

    logout(request)

    return redirect('/')