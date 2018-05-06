"""The main application's URLs."""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('profile', views.profile, name="profile"),
    path('logout', views.logout, name="logout"),
    path('new', views.new, name="new"),
    path('choose_style', views.choose_style, name="choose_style")
]
