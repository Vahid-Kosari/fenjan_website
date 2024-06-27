from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("run-linkedin/", views.linkedin_runner, name="linkedin_runner"),
]
