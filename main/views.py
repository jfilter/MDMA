from django.shortcuts import render
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .forms import InputImageForm


def index(request):
    return render(request, "index.html")


@login_required
def profile(request):
    return render(request, "profile.html")


@login_required
def my_input_images(request):
    return render(request, "profile.html")


@login_required
def my_output_images(request):
    return render(request, "profile.html")


@login_required
def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


@login_required
def new(request):
    if request.method == 'POST':
        form = InputImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('choose_style')
    else:
        form = InputImageForm()
    return render(request, 'new.html', {
        'form': form
    })

def choose_style(request):
    return render(request, "choose_style.html")