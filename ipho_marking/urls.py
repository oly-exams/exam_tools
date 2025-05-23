from django.urls import path, re_path

from . import views

app_name = "marking"
urlpatterns = [
    ## Delegation views
    path("", views.delegation_summary, name="delegation-summary"),
    path(
        "export/all",
        views.delegation_export,
        name="delegation-export-all",
    ),
    path(
        "export/exam/<int:exam_id>",
        views.delegation_export,
        name="delegation-export",
    ),
    path(
        "detail/<int:ppnt_id>/question/<int:question_id>",
        views.delegation_ppnt_view,
        name="delegation-ppnt-detail",
    ),
    path(
        "detail_all/question/<int:question_id>",
        views.delegation_view_all,
        name="delegation-all-detail",
    ),
    path(
        "detail/<int:ppnt_id>/question/<int:question_id>/edit",
        views.delegation_ppnt_edit,
        name="delegation-ppnt-detail-edit",
    ),
    path(
        "detail_all/question/<int:question_id>/edit",
        views.delegation_edit_all,
        name="delegation-all-detail-edit",
    ),
    path(
        "confirm/<int:question_id>",
        views.delegation_confirm,
        name="delegation-confirm",
    ),
    path(
        "confirm/final/<int:question_id>",
        views.delegation_confirm,
        name="delegation-final-confirm",
        kwargs={"final_confirmation": True},
    ),
    ## Markers
    re_path(
        r"^official/?$", views.official_marking_index, name="official-marking-index"
    ),
    path(
        "official/question/<int:question_id>",
        views.official_marking_index,
        name="official-marking-index-question",
    ),
    path(
        "official/question/<int:question_id>/template",
        views.create_marking_template,
        name="official-marking-template",
    ),
    path(
        "official/question/<int:question_id>/delegation/<int:delegation_id>",
        views.official_marking_detail,
        name="official-marking-detail",
    ),
    path(
        "official/question/<int:question_id>/delegation/<int:delegation_id>/confirmed",
        views.official_marking_confirmed,
        name="official-marking-confirmed",
    ),
    ## Moderations views
    re_path(r"^moderate/?$", views.moderation_index, name="moderation-index"),
    path(
        "moderate/question/<int:question_id>",
        views.moderation_index,
        name="moderation-index-question",
    ),
    path(
        "moderate/question/<int:question_id>/delegation/<int:delegation_id>",
        views.moderation_detail,
        name="moderation-detail",
    ),
    path(
        "moderate/question/<int:question_id>/delegation/<int:delegation_id>/confirmed",
        views.moderation_confirmed,
        name="moderation-confirmed",
    ),
    ##  staff views
    re_path(r"^staff/import/?$", views.import_exam, name="import-exam"),
    re_path(r"^staff/?$", views.summary, name="summary"),
    re_path(
        r"^staff/v(?P<version>\w)/participant/(?P<ppnt_id>\d+)/question/(?P<question_id>\d+)/edit$",
        views.staff_ppnt_detail,
        name="staff-ppnt-detail",
    ),
    path(
        "export-countries-to-moderate.csv",
        views.export_countries_to_moderate,
        name="countries-to-moderate",
    ),
    path("all/export.csv", views.export, name="export"),
    path(
        "all/export-final.csv",
        views.export_sql,
        name="export-total",
        kwargs={"versions": ["F"]},
    ),
    path("marking-submissions", views.marking_submissions, name="marking-submissions"),
    path("progress", views.progress, name="progress"),
    path("ranking", views.ranking, name="ranking"),
    path("export-ranking-csv", views.export_ranking_csv, name="export-ranking-csv"),
]
