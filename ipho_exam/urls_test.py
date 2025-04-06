from django.urls import re_path

from . import views_test

app_name = "test"
urlpatterns = [
    re_path(r"^$", views_test.index),
    re_path(r"^view$", views_test.view, name="view"),
    re_path(r"^edit$", views_test.edit, name="edit"),
    re_path(r"^inline$", views_test.inline_edit, name="inline"),
    re_path(r"^mathquill$", views_test.mathquill, name="mathquill"),
    re_path(
        r"^mathquill_toolbar$", views_test.mathquill_toolbar, name="mathquill_toolbar"
    ),
]
