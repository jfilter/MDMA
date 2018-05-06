"""The main application's URLs."""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('profile/', views.profile, name="profile"),
    path('logout/', views.logout, name="logout"),
    path('new/', views.new, name="new"),
    path('new/<int:input_image_id>/', views.choose_style, name="choose_style"),
    path('my_input_images/', views.my_input_images, name="my_input_images")
]
