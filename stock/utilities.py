import pytz
from django.utils import timezone


def convert_to_localtime(utctime):
    fmt = '%b %d, %Y, %I:%M %p'
    utc = utctime.replace(tzinfo=pytz.UTC)
    local = utc.astimezone(timezone.get_current_timezone())
    return local.strftime(fmt)
