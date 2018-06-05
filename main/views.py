import base64
import os

import shortuuid
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers import serialize
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import ChooseParamtersForm, InputImageForm, UpdateInputImageForm, UpdateVisiblityJobForm
from .models import (
    STATUS_FINISHED, STATUS_WATING, STATUS_WORKING, VISIBILITY_PRIVATE, VISIBILITY_PUBLIC, VISIBILITY_UNLISTED,
    InputImage, Job, StyleImage,
)


def index(request):
    jobs = Job.objects.filter(visibility=VISIBILITY_PUBLIC, status=STATUS_FINISHED).order_by(
        '-job_finished_at').all()[:9]

    return render(request, "index.html", {'jobs': jobs})


def about(request):
    return render(request, "pages/about.html")


def legal(request):
    return render(request, "pages/legal.html")


def valid_basic_auth(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    token_type, _, credentials = auth_header.partition(' ')

    username = os.getenv("VERY_SECRET_BASIC_AUTH_USERNAME")
    password = os.getenv("VERY_SECRET_BASIC_AUTH_PASSWORD")

    # not sure if this has to be done like this
    u_p_str = username + ':' + password
    expected = base64.b64encode(u_p_str.encode('ascii')).decode()

    return token_type == 'Basic' and credentials == expected


@login_required
def profile(request):
    return render(request, "profile.html")


@login_required
def logout(request):
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

            # hotfix to change .png to .jpg (because we converted them)
            if s.image.url.lower().endswith('.png'):
                filename_without_ext = s.image.url.split('/')[-1].split('.')[0]
                s.image = f"input/{filename_without_ext}.jpg"
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
    paginator = Paginator(style_images_list, 20)
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
            s.uuid = shortuuid.ShortUUID().random(length=50)
            s.save()
            return redirect('/artworks/' + str(s.id))
    else:
        form = ChooseParamtersForm()
    return render(request, 'choose_parameters.html', {
        'form': form, 'style_image': style_image, 'input_image': input_image
    })


def input_images(request):
    image_list = InputImage.objects.filter(visibility=VISIBILITY_PUBLIC)
    paginator = Paginator(image_list, 20)

    page = request.GET.get('page')
    images = paginator.get_page(page)

    style_image_id = request.GET.get('style_image')

    return render(request, 'input_images.html', {'images': images, 'public': True, 'style_image_id': style_image_id},)


@login_required
def my_input_images(request):
    image_list = InputImage.objects.filter(user=request.user)
    paginator = Paginator(image_list, 20)

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
            input_image.title = form.cleaned_data['title']
            input_image.description = form.cleaned_data['description']
            input_image.public_domain = form.cleaned_data['public_domain']
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

        jobs_list = Job.objects.filter(user=request.user).order_by(
            '-created_at')
    else:
        jobs_list = Job.objects.filter(visibility=VISIBILITY_PUBLIC).order_by(
            '-created_at')

    paginator = Paginator(jobs_list, 9 * 3)

    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    return render(request, 'jobs.html', {'jobs': jobs, 'my': my is not None})


def show_unlisted_job(request, job_uuid):
    job = Job.objects.get(uuid=job_uuid)

    if job.visibility == VISIBILITY_PRIVATE:
        raise PermissionDenied

    return render(request, 'show_job.html', {'job': job})


@require_GET
def get_jobs(request):
    if not valid_basic_auth(request):
        return HttpResponse(status=401)

    limit = int(request.GET.get('num', 10))

    with transaction.atomic():
        waiting_jobs = Job.objects.filter(
            status=STATUS_WATING)[:limit]

        # we have to do this here before the update or the jobs are lost
        waiting_jobs_list = list(waiting_jobs)

        Job.objects.filter(id__in=waiting_jobs).update(job_started_at=timezone.now(),
                                                       status=STATUS_WORKING)

    data = serialize('json', waiting_jobs_list, fields=(
        'pk', 'style_weight', 'input_image', 'style_image'), use_natural_foreign_keys=True)

    return JsonResponse({'jobs': data})


@csrf_exempt
@require_POST
def upload_finished_job(request, job_id):
    if not valid_basic_auth(request):
        return HttpResponse(status=401)

    # can't proceed without files
    if len(request.FILES) != 1:
        return HttpResponse(status=422)

    job = Job.objects.get(pk=job_id)

    job.output_image.save(name='outputimage.jpg',
                          content=request.FILES['file'])
    job.status = STATUS_FINISHED
    job.job_finished_at = timezone.now()
    job.save()

    # successfully processed the request
    return HttpResponse(status=204)
