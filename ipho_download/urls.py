
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, {'url': '', 'type': 'd'},name='main'),
    url(r'^(?P<type>[fd])/(?P<url>.*)$', views.main, name='path'),
]
