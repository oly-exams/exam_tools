from django.urls import path

from . import views

app_name = "print"
urlpatterns = [
    path("", views.main, name="main"),
]
