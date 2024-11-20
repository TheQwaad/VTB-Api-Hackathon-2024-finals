from django.views.debug import ExceptionReporter
from pathlib import Path


class CustomExceptionReporter(ExceptionReporter):
    def html_template_path(self):
        pass # todo render template (and check api error format if changes)
