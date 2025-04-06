from django.urls import path, re_path

from . import views

app_name = "download"
urlpatterns = [
    path("", views.main, {"url": "", "type": "d"}, name="main"),
    re_path(r"add_directory/(?P<url>.*)$", views.add_new_directory, name="add-dir"),
    re_path(r"add_file/(?P<url>.*)$", views.add_new_file, name="add-file"),
    re_path(r"remove/(?P<url>.*)$", views.remove, name="remove"),
    re_path(r"^(?P<type>[fd])/(?P<url>.*)$", views.main, name="path"),
]
