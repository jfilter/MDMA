from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404


from .forms import InputImageForm, ChooseParamtersForm, UpdateVisiblityJobForm, UpdateInputImageForm
from .models import InputImage, StyleImage, Job, VISIBILITY_UNLISTED, VISIBILITY_PUBLIC, VISIBILITY_PRIVATE


def index(request):
    jobs = Job.objects.filter(visibility=VISIBILITY_PUBLIC).all()[:9]

    return render(request, "index.html", {'jobs': jobs})


@login_required
def profile(request):
    return render(request, "profile.html")


@login_required
def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


@login_required
def upload_input_image(request):
    if request.method == 'POST':
        form = InputImageForm(request.POST, request.FILES)
        if form.is_valid():
            s = form.save()
            # first save form, then add current user
            s.user = request.user
            s.save()
            return redirect('/new/' + str(s.id))
    else:
        form = InputImageForm()

    style_image = request.GET.get('style_image')
    additional = '' if style_image is None else '?style_image=' + style_image

    return render(request, 'new.html', {
        'form': form, 'additional': additional
    })


@login_required
def choose_style(request, input_image_id):
    input_image = InputImage.objects.get(pk=input_image_id)

    if request.user != input_image.user:
        raise PermissionDenied

    style_images_list = StyleImage.objects.all()
    paginator = Paginator(style_images_list, 5)
    page = request.GET.get('page')
    style_images = paginator.get_page(page)

    return render(request, "choose_style.html", {'input_image': input_image, 'style_images': style_images})


@login_required
def choose_parameters(request, input_image_id, style_image_id):
    input_image = InputImage.objects.get(pk=input_image_id)
    if request.user != input_image.user:
        raise PermissionDenied
    style_image = StyleImage.objects.get(pk=style_image_id)

    if request.method == 'POST':
        form = ChooseParamtersForm(request.POST)
        if form.is_valid():
            s = form.save()
            # first save form, then add current user
            s.user = request.user
            s.input_image = input_image
            s.style_image = style_image
            s.save()
            return redirect('/artwork/' + str(s.id))
        print('not valid')
    else:
        form = ChooseParamtersForm()
    return render(request, 'choose_parameters.html', {
        'form': form, 'style_image': style_image, 'input_image': input_image
    })


def input_images(request):
    image_list = InputImage.objects.filter(visibility=VISIBILITY_PUBLIC)
    paginator = Paginator(image_list, 10)

    page = request.GET.get('page')
    images = paginator.get_page(page)

    style_image_id = request.GET.get('style_image')

    return render(request, 'input_images.html', {'images': images, 'public': True, 'style_image_id': style_image_id},)


@login_required
def my_input_images(request):
    image_list = InputImage.objects.filter(user=request.user)
    paginator = Paginator(image_list, 10)

    page = request.GET.get('page')
    images = paginator.get_page(page)

    style_image_id = request.GET.get('style_image')

    return render(request, 'input_images.html', {'images': images, 'style_image_id': style_image_id})


@login_required
def show_input_image(request, input_image_id):
    form = None
    input_image = InputImage.objects.get(pk=input_image_id)

    if input_image.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = UpdateInputImageForm(request.POST)

        if form.is_valid():
            input_image.visibility = form.cleaned_data['visibility']
            input_image.copyright_notice = form.cleaned_data['copyright_notice']
            input_image.description = form.cleaned_data['description']
            input_image.save()
    else:
        form = UpdateInputImageForm(instance=input_image)

    return render(request, 'show_input_image.html', {'input_image': input_image, 'form': form})


def show_public_job(request, job_id):
    form = None
    job = Job.objects.get(pk=job_id)

    if job.visibility != VISIBILITY_PUBLIC and job.user != request.user:
        raise PermissionDenied

    if job.user == request.user:
        if request.method == 'POST':
            form = UpdateVisiblityJobForm(request.POST)

            if form.is_valid():
                job.visibility = form.cleaned_data['visibility']
                job.save()
        else:
            form = UpdateVisiblityJobForm(instance=job)

    return render(request, 'show_job.html', {'job': job, 'form': form})


def jobs(request):
    my = request.GET.get('my')

    if my is not None:
        if request.user is None:
            raise PermissionDenied

        jobs_list = Job.objects.filter(user=request.user)
    else:
        jobs_list = Job.objects.filter(visibility=VISIBILITY_PUBLIC)

    paginator = Paginator(jobs_list, 10)

    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    return render(request, 'jobs.html', {'jobs': jobs, 'my': my is not None})


def show_unlisted_job(request, job_uuid):
    job = Job.objects.get(uuid=job_uuid)

    if job.visibility == VISIBILITY_PRIVATE:
        raise PermissionDenied

    return render(request, 'show_job.html', {'job': job})
