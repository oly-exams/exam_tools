from django.urls import path

from . import views

app_name = "control"
urlpatterns = [
    path("cockpit", views.cockpit, name="cockpit"),
    path("cockpit/<int:exam_id>", views.cockpit, name="cockpit-id"),
    path(
        "cockpit/<int:exam_id>/changed-phase",
        views.cockpit,
        kwargs={"changed_phase": True},
        name="cockpit-changed-phase",
    ),
    path(
        "cockpit/<int:exam_id>/deleted",
        views.cockpit,
        kwargs={"deleted_phase": True},
        name="cockpit-deleted-phase",
    ),
    path(
        "cockpit/switch-phase/<int:exam_id>/<int:phase_id>",
        views.switch_phase,
        name="switch-phase",
    ),
    path("cockpit/exam_history/<int:exam_id>", views.exam_history, name="exam-history"),
    path("phase/add/<int:exam_id>", views.add_edit_phase, name="add-phase"),
    path("phase/edit/<int:phase_id>", views.add_edit_phase, name="edit-phase"),
    path("phase/delete/<int:phase_id>", views.delete_phase, name="delete-phase"),
    path("phase/summary", views.exam_phase_summary, name="exam-phase-summary"),
]
