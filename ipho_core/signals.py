import logging
import time

from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from ipware import get_client_ip

# this is not the right place for this, but for now I put it here
if getattr(settings, "RECORD_USER_LOGIN_LOGOUT_IPS"):
    LOGGER = logging.getLogger("exam_tools")

    def log_logged_in(
        sender, user, request, **kwargs
    ):  # pylint: disable=unused-argument
        LOGGER.info(
            "%s User %s successfully logged in at %s",
            user,
            get_client_ip(request)[0],
            time.strftime("%m/%d/%Y %H:%M:%S"),
        )

    def log_logged_out(
        sender, user, request, **kwargs
    ):  # pylint: disable=unused-argument
        LOGGER.info(
            "%s User %s successfully logged out at %s",
            user,
            get_client_ip(request)[0],
            time.strftime("%m/%d/%Y %H:%M:%S"),
        )

    user_logged_in.connect(log_logged_in)
    user_logged_out.connect(log_logged_out)
