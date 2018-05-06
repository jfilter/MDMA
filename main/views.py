from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


from .forms import InputImageForm
from .models import InputImage


def index(request):
    return render(request, "index.html")


@login_required
def profile(request):
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
            s = form.save()
            # first save form, then add current user
            s.user = request.user
            s.save()
            return redirect('new/' + str(s.id))
    else:
        form = InputImageForm()
    return render(request, 'new.html', {
        'form': form
    })


@login_required
def choose_style(request, input_image_id):
    input_image = InputImage.objects.get(pk=input_image_id)
    if request.user != input_image.user:
        raise PermissionDenied

    return render(request, "choose_style.html", {'input_image': input_image})


@login_required
def my_input_images(request):
    image_list = InputImage.objects.filter(user=request.user)
    paginator = Paginator(image_list, 10)

    page = request.GET.get('page')
    images = paginator.get_page(page)
    return render(request, 'my_input_images.html', {'images': images})
