from django.core.exceptions import PermissionDenied
from datetime import datetime, date, time
from django.http import HttpResponseForbidden
# from django.views.defaults import permission_denied


def check_market_time(function):
    def wrap(request, *args, **kwargs):
        value = function(request, *args, **kwargs)
        start_time = time(9, 15, 00).replace(microsecond=0)
        end_time = time(15, 30, 00).replace(microsecond=0)
        current_time = datetime.now().time().replace(microsecond=0)

        if current_time >= start_time and current_time <= end_time:

            return value
        else:
            raise PermissionDenied(request)
    #wrap.__doc__ = function.__doc__
    #swrap.__name__ = function.__name__
    return wrap
