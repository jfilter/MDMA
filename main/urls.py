"""The main application's URLs."""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('about/', views.about, name="about"),
    path('legal/', views.legal, name="legal"),
    path('profile/', views.profile, name="profile"),
    path('logout/', views.logout, name="logout"),
    path('new/', views.upload_input_image, name="new"),
    path('new/<int:input_image_id>/', views.choose_style, name="choose_style"),
    path('new/<int:input_image_id>/<int:style_image_id>/',
         views.choose_parameters, name="choose_parameters"),
    path('artworks/', views.jobs, name="artworks"),
    path('artworks/<int:job_id>/', views.show_public_job, name="artwork"),
    path('artworks/<slug:job_uuid>/',
         views.show_unlisted_job, name="unlisted_job"),
    path('my_input_images/', views.my_input_images, name="my_input_images"),
    path('input_images/', views.input_images, name="input_images"),
    path('input_images/<int:input_image_id>',
         views.show_input_image, name="input_image"),
    path('get_jobs/', views.get_jobs, name="get_jobs"),
    path('upload_finished_job/<int:job_id>/',
         views.upload_finished_job, name="upload_finished_job"),
    path('num_open_jobs/', views.get_num_open_jobs)
]
