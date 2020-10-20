#!/usr/bin/env python

# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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

from decimal import Decimal

from ipho_exam import qquery
from ipho_exam.models import Question
from ipho_exam.qml import QMLquestion, QMLpart, QMLsubquestion, QMLsubanswer, make_qml

__all__ = [
    "check_version",
    "check_exam",
    "check_question_answer_consistency",
    "check_sum_consistency",
]

OFFICIAL_LANGUAGE_PK = 1

NESTING_LEVELS = [(QMLquestion), (QMLpart), (QMLsubquestion, QMLsubanswer)]


class PointValidationError(ValueError):
    pass


def check_version(version):
    """
    Check a given version node.
    """
    question = version.question
    code = question.code
    if code == "G":
        return
    check_sum_consistency(version)
    other_code = ({"Q", "A"} - {code}).pop()
    q_type = {"Q": "question", "A": "answer"}
    try:
        other_question = Question.objects.get(
            exam=question.exam, code=other_code, position=question.position
        )
    except Question.DoesNotExist:
        raise PointValidationError(
            "The {} sheet corresponding to this {} does not exist.".format(
                q_type[other_code], q_type[code]
            )
        )
    try:
        other_version = qquery.latest_version(
            other_question.pk, lang_id=OFFICIAL_LANGUAGE_PK
        ).node
    except IndexError:
        raise PointValidationError(
            "The {} sheet corresponding to this {} does not have a published version.".format(
                q_type[other_code], q_type[code]
            )
        )
    check_question_answer_consistency(version, other_version)


def check_exam(exam):
    """
    Check the sum and question / answer consistency of all questions in the
    given exam.
    """
    all_questions = Question.objects.filter(exam=exam, code__in=["Q", "A"]).order_by(
        "position"
    )
    for q1, q2 in zip(all_questions[::2], all_questions[1::2]):
        version_1 = qquery.latest_version(q1.pk, lang_id=OFFICIAL_LANGUAGE_PK).node
        version_2 = qquery.latest_version(q2.pk, lang_id=OFFICIAL_LANGUAGE_PK).node
        check_sum_consistency(version_1)
        check_sum_consistency(version_2)
        check_question_answer_consistency(version_1, version_2)


def check_question_answer_consistency(version_node_1, version_node_2):
    """
    Check that the points in the two question given (question / answer sheet)
    are the same.
    """

    assert version_node_1.question.exam == version_node_2.question.exam
    assert version_node_1.question.position == version_node_1.question.position
    assert {version_node_1.question.code, version_node_2.question.code} == {"Q", "A"}
    qml_1 = make_qml(version_node_1)
    qml_2 = make_qml(version_node_2)

    flat_nodes_1 = [
        node for node in _get_flat_node_list(qml_1) if "points" in node.attributes
    ]
    flat_nodes_2 = [
        node for node in _get_flat_node_list(qml_2) if "points" in node.attributes
    ]
    if len(flat_nodes_1) != len(flat_nodes_2):
        raise PointValidationError(
            "'{}' and '{}' in '{}' do not have the same number of objects with a 'points' attribute ({}, {})".format(
                version_node_1.question.name,
                version_node_2.question.name,
                version_node_1.question.exam.name,
                len(flat_nodes_1),
                len(flat_nodes_2),
            )
        )
    for node1, node2 in zip(flat_nodes_1, flat_nodes_2):
        p1 = _get_points(node1)
        p2 = _get_points(node2)
        if p1 != p2:
            raise PointValidationError(
                "The number of points of {} '{}' ({}) and {} '{}' ({}) do not match".format(
                    _get_type_name(node1),
                    node1.attributes["id"],
                    p1,
                    _get_type_name(node2),
                    node2.attributes["id"],
                    p2,
                )
            )


def check_sum_consistency(version_node):
    """
    Check that the points of a question are internally consistent, i.e. the sum
    of points of 'sub-tasks' matches the points of a 'task'.
    """
    qml_tree = make_qml(version_node)

    nested_nodes = _get_nested_nodes(qml_tree)
    _check_nested_sum_consistency(nested_nodes)


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
    res = {}
    while flat_nodes_reversed:
        candidate = flat_nodes_reversed.pop()
        candidate_nesting_level = _get_nesting_level(candidate)
        if candidate_nesting_level is None:
            continue
        elif candidate_nesting_level == nesting_level:
            res[candidate] = _wrap_nodes(
                flat_nodes_reversed, nesting_level=candidate_nesting_level + 1
            )
        elif candidate_nesting_level < nesting_level:
            flat_nodes_reversed.append(candidate)
            return res
        else:
            assert False
    return res


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
    return _check_sum_consistency_recursive(key, value)


def _check_sum_consistency_recursive(root_node, children_dict):
    root_points = _get_points(root_node)
    if children_dict:
        sum_points = sum(
            _check_sum_consistency_recursive(key, value)
            for key, value in children_dict.items()
        )
        if sum_points != root_points:
            raise PointValidationError(
                "The number of points for {} '{}' ({}) does not match the sum of its sub-parts ({})".format(
                    _get_type_name(root_node),
                    root_node.attributes["id"],
                    root_points,
                    sum_points,
                )
            )
    return root_points


def _get_points(node):
    try:
        return Decimal(node.attributes["points"])
    except KeyError:
        raise PointValidationError(
            "{} {} is missing the 'points' attribute.".format(
                _get_type_name(node), node.attributes["id"]
            )
        )


def _get_type_name(node):
    cls = type(node)
    return cls.default_heading or cls.display_name
