from django.urls import path

from . import views

app_name = "poll"
urlpatterns = [
    # staff urls
    path("staff/", views.staff_index, name="staff-index"),
    path("staff/room/<int:room_id>", views.staff_index, name="staff-index_room"),
    path(
        "staff/room/<int:room_id>/partials/<slug:qtype>",
        views.staff_index_partial,
        name="staff-index-partials-room",
    ),
    path(
        "staff/room/partials/<slug:qtype>",
        views.staff_index_partial,
        name="staff-index-partials",
    ),
    path(
        "staff/voting/<int:voting_pk>/set/result/<int:result>",
        views.staff_set_result,
        name="staff-set-result",
    ),
    path(
        "staff/voting/<int:voting_pk>/set/impl/<int:impl>",
        views.staff_set_impl,
        name="staff-set-impl",
    ),
    path("voting/detail/<int:voting_pk>/", views.voting_details, name="voting"),
    path(
        "voting/large/<int:voting_pk>/",
        views.voting_large,
        name="voting_large",
    ),
    path("voting/add/room/<int:room_id>", views.add_voting, name="add-voting-in-room"),
    path("voting/add/main", views.add_voting, name="add-voting"),
    path(
        "voting/<int:voting_pk>/delete/",
        views.delete_voting,
        name="delete-voting",
    ),
    path(
        "voting/<int:voting_pk>/edit/",
        views.edit_voting,
        name="edit-voting",
    ),
    path("voting/<int:voting_pk>/", views.set_end_date, name="set-end-date"),
    path(
        "voting/<int:voting_pk>/add_minutes/<int:minutes>/",
        views.add_minutes,
        name="add-minutes",
    ),
    path(
        "voting/<int:voting_pk>/close",
        views.close_voting,
        name="close-voting",
    ),
    path(
        "voting/<int:voting_pk>/reopen",
        views.reopen_voting,
        name="reopen-voting",
    ),
    path("room/edit/<int:room_id>", views.edit_room, name="edit-room"),
    # delegation urls
    path("", views.voter_index, name="voter-index"),
    path("room/<int:room_id>", views.voter_index, name="voter-index_room"),
    path("err/<int:err_id>", views.voter_index, name="voter-index_err"),
    path(
        "room/<int:room_id>/err/<int:err_id>",
        views.voter_index,
        name="voter-index_room_err",
    ),
    path("voted/room/<int:room_id>", views.voted, name="voted_room"),
    path("voted/", views.voted, name="voted"),
]
