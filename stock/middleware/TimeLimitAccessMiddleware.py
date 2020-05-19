from django.core.exceptions import PermissionDenied
from datetime import datetime, date, time


class TimeLimitMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Handle new-style middleware here."""
        response = self.process_request(request)
        if response is None:
            response = self.get_response(request)
        print("resposne  ", response)
        return response
        # response = self.process_response(request, response)
        # if not response:
        #     response = self.get_response(request)
        # return response

    def process_request(self, request):
        start_time = time(9, 15, 00).replace(microsecond=0)
        end_time = time(23, 30, 00).replace(microsecond=0)
        current_time = datetime.now().time().replace(microsecond=0)
        print("current time is ", current_time)
        print('start_time ', start_time, " end_time ", end_time )
        if current_time >= start_time and current_time <= end_time:
            # if in current time do nothing
            print("inside limit")
            print("#"*100)
            return None
        else:
            print("*"*100)
            raise PermissionDenied
