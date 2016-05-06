from django.conf.urls import url

from . import views

urlpatterns = [
## Delegation views
    url(r'^/?$', views.delegation_summary, name='delegation-summary'),
    url(r'^detail/(?P<stud_id>\d+)/exam/(?P<exam_id>\d+)/question/(?P<question_id>\d+)$', views.delegation_stud_detail, name='delegation-stud-detail'),
    url(r'^confirm/(?P<exam_id>\d+)$', views.delegation_confirm, name='delegation-confirm'),

## Markers / staff views
    url(r'^import/?$', views.import_exam, name='import-exam'),
    url(r'^all/?$', views.summary, name='summary'),
    url(r'^all/export.csv$', views.export, name='export'),
]
