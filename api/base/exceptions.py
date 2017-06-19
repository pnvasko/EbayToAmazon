# -*- coding: utf-8 -*-
import sys
import traceback


def tracebackinfo():
    traceback_template = '''Traceback (most recent call last):
      File "%(filename)s", line %(lineno)s, in %(name)s
    %(type)s: %(message)s\n'''

    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_details = {
        'filename': exc_traceback.tb_frame.f_code.co_filename,
        'lineno': exc_traceback.tb_lineno,
        'name': exc_traceback.tb_frame.f_code.co_name,
        'type': exc_type.__name__,
        'message': exc_value.message,  # or see traceback._some_str()
    }
    del (exc_type, exc_value, exc_traceback)
    err = traceback_template % traceback_details
    return err


class ApiBaseException(Exception):
    def __init__(self, message, chain=None):
        super(ApiBaseException, self).__init__(message)
        self.message = message
        self.chain = chain

    @property
    def traceback(self):
        return traceback.format_exc()

    def __str__(self):
        return self.message
