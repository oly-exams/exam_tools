from django.conf.urls import url

from . import views

urlpatterns = [
## Delegation views
    url(r'^/?$', views.delegation_summary, name='delegation-summary'),
    url(r'^detail/(?P<stud_id>\d+)/question/(?P<question_id>\d+)$', views.delegation_stud_detail, name='delegation-stud-detail'),
    url(r'^detail/(?P<stud_id>\d+)/question/(?P<question_id>\d+)/edit$', views.delegation_stud_detail, name='delegation-stud-detail-edit'),
    url(r'^confirm/(?P<exam_id>\d+)$', views.delegation_confirm, name='delegation-confirm'),

## Markers
# TODO
## Moderations views
    url(r'^moderate/?$', views.moderation_index, name='moderation-index'),
    url(r'^moderate/question/(?P<question_id>\d+)$', views.moderation_index, name='moderation-index-question'),
    url(r'^moderate/question/(?P<question_id>\d+)/delegation/(?P<delegation_id>\d+)$', views.moderation_detail, name='moderation-detail'),
    url(r'^moderate/question/(?P<question_id>\d+)/delegation/(?P<delegation_id>\d+)/confirmed$', views.moderation_confirmed, name='moderation-confirmed'),

##  staff views
    url(r'^staff/import/?$', views.import_exam, name='import-exam'),
    url(r'^staff/?$', views.summary, name='summary'),
    url(r'^staff/v(?P<version>\w)/student/(?P<stud_id>\d+)/question/(?P<question_id>\d+)/edit$', views.staff_stud_detail, name='staff-stud-detail'),

    url(r'^all/export.csv$', views.export, name='export'),
]
