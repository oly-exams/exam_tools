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

# pylint: disable = consider-using-f-string

import logging
from hashlib import md5

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseNotModified, HttpResponseRedirect
from django.urls import reverse

from ipho_exam import tasks

logger = logging.getLogger("ipho_exam.cached_responses")

CACHE_PREFIX = getattr(settings, "CACHE_CACHED_RESPONSES_PREFIX", "cached-responses")
CACHE_TIMEOUT = getattr(settings, "CACHE_CACHED_RESPONSES_TIMEOUT", 600)  # 10 min


def compile_tex(request, body, ext_resources=tuple(), filename="question.pdf"):
    etag = md5(body.encode("utf8")).hexdigest()
    if request.META.get("HTTP_IF_NONE_MATCH", "") == etag:
        logger.debug(
            "Request to compile_tex contains valid etag. HttpResponseNotModified will be sended."
        )
        return HttpResponseNotModified()

    logger.debug("Request to compile_tex does not contain valid etag")

    cache_key = "{}:{}:{}".format(CACHE_PREFIX, "compile_tex", etag)
    task_id = cache.get(cache_key)

    if task_id is None:
        logger.debug(
            "The tex body of compile_tex is not in the cache. A new async task will be started."
        )
        job = tasks.compile_tex.delay(body, ext_resources, filename, etag)
        task_id = job.id
        cache.set(cache_key, task_id, CACHE_TIMEOUT)
    return HttpResponseRedirect(reverse("exam:pdf-task", args=[task_id]))


def compile_tex_diff(
    request, old_body, new_body, ext_resources=tuple(), filename="question.pdf"
):
    etag = md5((old_body + new_body).encode("utf8")).hexdigest()
    if request.META.get("HTTP_IF_NONE_MATCH", "") == etag:
        logger.debug(
            "Request to compile_tex_diff contains valid etag. HttpResponseNotModified will be sended."
        )
        return HttpResponseNotModified()

    logger.debug("Request to compile_tex_diff does not contain valid etag")

    cache_key = "{}:{}:{}".format(CACHE_PREFIX, "compile_tex_diff", etag)
    task_id = cache.get(cache_key)

    if task_id is None:
        logger.debug(
            "The tex body of compile_tex is not in the cache. A new async task will be started."
        )
        job = tasks.compile_tex_diff.delay(
            old_body, new_body, ext_resources, filename, etag
        )
        task_id = job.id
        cache.set(cache_key, task_id, CACHE_TIMEOUT)

    return HttpResponseRedirect(reverse("exam:pdf-task", args=[task_id]))
