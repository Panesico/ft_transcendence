# views.py
import os
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from authuser.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from authuser.forms import SignUpForm, LogInForm
import logging
logger = logging.getLogger(__name__)


def get_logout(request):
    logger.debug("")
    logger.debug("get_logout")

    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_logout XMLHttpRequest")
        return render(request, 'fragments/home_fragment.html')
    return redirect('home')

def post_login(request):
    logger.debug("")
    logger.debug("post_login")
    if request.method == 'POST':
        logger.debug("post_login > POST")
        form = LogInForm(request, data=request.POST)
        logger.debug(form)
        if form.is_valid():
            logger.debug("post_login > POST > form.is_valid")
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            logger.debug("post_login > POST > form NOT valid")
            messages.error(request, 'Invalid username or password.')
    else:
        logger.debug("post_login > not POST returning 405")
        return render(request, 'partials/405.html', status=405)
    
    form = LogInForm()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("post_login returning fragment")
        return render(request, 'fragments/login_fragment.html', {'form': form})
    logger.debug("post_login returning")
    logger.debug("form.errors:")
    logger.debug(form.errors) 
    return render(request, 'partials/login.html', {'form': form})

def post_signup(request):
    logger.debug("")
    logger.debug("post_signup")
    logger.debug(request)
    if request.method == 'POST':
        logger.debug("POST post_signup")
        logger.debug(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            logger.debug("POST post_signup form.is_valid")
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Log the user in automatically after signup
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Sign up successful!')
                return redirect('home')
        else:
            logger.debug("POST post_signup NOT form.is_valid")
            logger.debug("form.errors:")
            logger.debug(form.errors) 
            messages.error(request, 'Please correct the error below.')
    else:
        logger.debug("post_signup > not POST returning 405")
        return render(request, 'partials/405.html', status=405)

    form = SignUpForm()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("post_signup returning fragment")
        return render(request, 'fragments/signup_fragment.html', {'form': form})
    logger.debug("post_signup returning")
    logger.debug("form.errors:")
    logger.debug(form.errors) 
    return render(request, 'partials/signup.html', {'form': form})
