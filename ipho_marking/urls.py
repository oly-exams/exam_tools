from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^import/?$', views.import_exam, name='import-exam'),
    url(r'^all/?$', views.summary, name='summary'),
    url(r'^all/export.csv$', views.export, name='export'),
]
