#!/usr/bin/env python

# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=consider-using-f-string

from decimal import Decimal

from django.http.response import Http404
from django.conf import settings

from ipho_exam import qquery
from ipho_exam.models import Question, VersionNode
from ipho_exam.qml import QMLquestion, QMLpart, QMLsubquestion, QMLsubanswer, make_qml

__all__ = [
    "check_version",
    "check_exam",
    "check_question_answer_consistency",
    "check_sum_consistency",
]

OFFICIAL_LANGUAGE_PK = 1

NESTING_LEVELS = [(QMLquestion), (QMLpart), (QMLsubquestion, QMLsubanswer)]

ALLOW_NEGATIVE_MARKS = getattr(settings, "ALLOW_NEGATIVE_MARKS", False)


class PointValidationError(ValueError):
    pass


def check_version(version, other_question_status=("C", "S")):
    """
    Check a given version node.
    """
    error_msg_list = []
    question = version.question
    code = question.code
    if code == "G":
        return (version, None)
    error_msg_list += check_sum_consistency(version)
    error_msg_list += check_min_max_consistency(version)

    other_code = ({"Q", "A"} - {code}).pop()
    q_type = {"Q": "question", "A": "answer"}
    try:
        other_question = Question.objects.get(
            exam=question.exam, code=other_code, position=question.position
        )
    except Question.DoesNotExist:
        error_msg_list.append(
            "The {} sheet corresponding to this {} sheet does not exist.".format(
                q_type[other_code], q_type[code]
            )
        )
    try:
        qquery.latest_version(
            other_question.pk,
            lang_id=OFFICIAL_LANGUAGE_PK,
            status=dict(VersionNode.STATUS_CHOICES).keys(),
        )  # Check whether there are any versions
    except Http404:
        error_msg_list.append(
            "The {} sheet corresponding to this {} does not have any version.".format(
                q_type[other_code], q_type[code]
            )
        )
    try:
        other_version = qquery.latest_version(
            other_question.pk,
            lang_id=OFFICIAL_LANGUAGE_PK,
            status=other_question_status,
        ).node  # select the lastet version which is in other_question_status
    except Http404:
        error_msg_list.append(
            "The {} sheet corresponding to this {} does not have a version with one of the following status {}.".format(
                q_type[other_code],
                q_type[code],
                [
                    dict(VersionNode.STATUS_CHOICES).get(st)
                    for st in other_question_status
                ],
            )
        )

    error_msg_list += check_question_answer_consistency(version, other_version)

    if error_msg_list:
        raise PointValidationError("<li>".join(error_msg_list))

    return (version, other_version)


def check_exam(exam):
    """
    Check the sum and question / answer consistency of all questions in the
    given exam.
    """
    error_msg_list = []

    all_questions = Question.objects.filter(exam=exam, code__in=["Q", "A"]).order_by(
        "position"
    )
    for que1, que2 in zip(all_questions[::2], all_questions[1::2]):
        version_1 = qquery.latest_version(que1.pk, lang_id=OFFICIAL_LANGUAGE_PK).node
        version_2 = qquery.latest_version(que2.pk, lang_id=OFFICIAL_LANGUAGE_PK).node
        error_msg_list += check_sum_consistency(version_1)
        error_msg_list += check_sum_consistency(version_2)
        error_msg_list += check_min_max_consistency(version_1)
        error_msg_list += check_min_max_consistency(version_2)
        error_msg_list += check_question_answer_consistency(version_1, version_2)

    if error_msg_list:
        raise PointValidationError("\n".join(error_msg_list))


def check_question_answer_consistency(version_node_1, version_node_2):
    """
    Check that the points in the two question given (question / answer sheet)
    are the same.
    """
    error_msg_list = []

    assert version_node_1.question.exam == version_node_2.question.exam
    assert version_node_1.question.position == version_node_1.question.position
    assert {version_node_1.question.code, version_node_2.question.code} == {"Q", "A"}

    qml_1 = make_qml(version_node_1)
    qml_2 = make_qml(version_node_2)

    flat_nodes_1 = [
        node
        for node in _get_flat_node_list(qml_1)
        if ("min_points" in node.attributes or "max_points" in node.attributes)
    ]
    flat_nodes_2 = [
        node
        for node in _get_flat_node_list(qml_2)
        if ("min_points" in node.attributes or "max_points" in node.attributes)
    ]
    if len(flat_nodes_1) != len(flat_nodes_2):
        error_msg_list.append(
            "'{} v{}' and '{} v{}' in '{}' do not have the same number of objects with a 'points' attribute ({}, {})".format(
                version_node_1.question.name,
                version_node_1.version,
                version_node_2.question.name,
                version_node_2.version,
                version_node_1.question.exam.name,
                len(flat_nodes_1),
                len(flat_nodes_2),
            )
        )
    for node1, node2 in zip(flat_nodes_1, flat_nodes_2):
        min_pts1, max_pts1, error_msg = _get_points(node1)
        if error_msg:
            error_msg_list.append(error_msg)
            return error_msg_list
        min_pts2, max_pts2, error_msg = _get_points(node2)
        if error_msg:
            error_msg_list.append(error_msg)
            return error_msg_list
        if min_pts1 != min_pts2:
            error_msg_list.append(
                "The minimum number of points of {} '{}' ({}) and {} '{}' ({}) do not match (in '{} v{}' and '{} v{}')".format(
                    _get_type_name(node1),
                    node1.attributes["id"],
                    min_pts1,
                    _get_type_name(node2),
                    node2.attributes["id"],
                    min_pts2,
                    version_node_1.question.name,
                    version_node_1.version,
                    version_node_2.question.name,
                    version_node_2.version,
                )
            )
        if max_pts1 != max_pts2:
            error_msg_list.append(
                "The maximum number of points of {} '{}' ({}) and {} '{}' ({}) do not match (in '{} v{}' and '{} v{}')".format(
                    _get_type_name(node1),
                    node1.attributes["id"],
                    max_pts1,
                    _get_type_name(node2),
                    node2.attributes["id"],
                    max_pts2,
                    version_node_1.question.name,
                    version_node_1.version,
                    version_node_2.question.name,
                    version_node_2.version,
                )
            )
    return error_msg_list


def check_min_max_consistency(version_node):
    """
    Check that the min and max points are consistent.
    """
    error_msg_list = []

    qml = make_qml(version_node)

    flat_nodes = [
        node
        for node in _get_flat_node_list(qml)
        if ("min_points" in node.attributes or "max_points" in node.attributes)
    ]

    for node in flat_nodes:
        min_pts, max_pts, error_msg = _get_points(node)
        if error_msg:
            error_msg_list.append(error_msg)
            return error_msg_list
        if not ALLOW_NEGATIVE_MARKS and min_pts < 0:
            error_msg_list.append(
                "The minimum '{}' number of points can not be negative in {} '{}' in '{} v{}'".format(
                    min_pts,
                    _get_type_name(node),
                    node.attributes["id"],
                    version_node.question.name,
                    version_node.version,
                )
            )
        if max_pts < min_pts:
            error_msg_list.append(
                "The maximum '{}' is smaller than the minimum '{}' number of points in {} '{}' in '{} v{}'".format(
                    max_pts,
                    min_pts,
                    _get_type_name(node),
                    node.attributes["id"],
                    version_node.question.name,
                    version_node.version,
                )
            )
    return error_msg_list


def check_sum_consistency(version_node):
    """
    Check that the points of a question are internally consistent, i.e. the sum
    of points of 'sub-tasks' matches the points of a 'task'.
    """
    error_msg_list = []
    qml_tree = make_qml(version_node)

    nested_nodes, error_msg_list_temp = _get_nested_nodes(qml_tree)
    error_msg_list += list(set(error_msg_list_temp))
    error_msg_list += _check_nested_sum_consistency(nested_nodes)
    return error_msg_list


def _get_nested_nodes(qml_node):
    """
    Wrap the given QML structure into a nested dict where nesting is given by
    the logical structure of the points.
    """
    nesting_level = _get_nesting_level(qml_node)
    assert nesting_level is not None
    flat_nodes_reversed = list(reversed(_get_flat_node_list(qml_node)))

    return _wrap_nodes(flat_nodes_reversed, nesting_level=nesting_level)


def _wrap_nodes(flat_nodes_reversed, nesting_level=0):
    error_msg_list = []
    res = {}
    while flat_nodes_reversed:
        candidate = flat_nodes_reversed.pop()
        candidate_nesting_level = _get_nesting_level(candidate)
        if candidate_nesting_level is None:
            continue
        if candidate_nesting_level == nesting_level:
            res[candidate], error_msg_list_temp = _wrap_nodes(
                flat_nodes_reversed, nesting_level=candidate_nesting_level + 1
            )
            error_msg_list += error_msg_list_temp
        elif candidate_nesting_level < nesting_level:
            flat_nodes_reversed.append(candidate)
            return res, error_msg_list
        else:
            error_msg_list.append("there might be missing 'parts' or 'tasks'")
    return res, error_msg_list


def _get_flat_node_list(qml_node):
    """
    Get a flat list of nodes in the given QML object.
    """
    res = [qml_node]
    if qml_node.has_children:
        for child in qml_node.children:
            res.extend(_get_flat_node_list(child))
    return res


def _get_nesting_level(qml_node):
    for i, types in enumerate(NESTING_LEVELS):
        if isinstance(qml_node, types):
            return i
    return None


def _check_nested_sum_consistency(root_dict):
    assert len(root_dict) == 1
    key, value = list(root_dict.items())[0]
    _, error_msg_list = _check_sum_consistency_recursive(key, value)
    return error_msg_list


def _check_sum_consistency_recursive(root_node, children_dict):
    error_msg_list = []
    _, root_max_points, error_msg = _get_points(root_node)
    if error_msg:
        error_msg_list.append(error_msg)
        return root_max_points, error_msg_list
    if children_dict:
        points_and_error_list = [
            _check_sum_consistency_recursive(key, value)
            for key, value in children_dict.items()
        ]
        error_msg_list += sum([item for _, item in points_and_error_list], [])
        sum_points = sum([item for item, _ in points_and_error_list])
        if sum_points != root_max_points:
            error_msg_list.append(
                "The number of points for {} '{}' ({}) does not match the sum of its sub-parts ({})".format(
                    _get_type_name(root_node),
                    root_node.attributes["id"],
                    root_max_points,
                    sum_points,
                )
            )
    return root_max_points, error_msg_list


def _get_points(node):
    try:
        return (
            Decimal(node.attributes["min_points"]),
            Decimal(node.attributes["max_points"]),
            "",
        )
    except KeyError:
        return (
            0,
            0,
            "{} {} is missing the 'min_points' or 'max_points' attribute.".format(
                _get_type_name(node), node.attributes["id"]
            ),
        )


def _get_type_name(node):
    cls = type(node)
    return cls.default_heading or cls.display_name
