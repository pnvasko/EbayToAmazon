# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
from sqlalchemy import create_engine
import logging
import logging.handlers
import datetime
from api.base import ApiBaseException


class BaseTaskException(ApiBaseException):
    def __str__(self):
        return 'Task error: {0}'.format(self.message)


def import_string(import_name, silent=False):
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            module = import_string(module_name)

        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)

    except ImportError as e:
        if not silent:
            raise BaseTaskException(e)


class BaseTasks(object):
    _db = None

    def __init__(self):
        self._config = self.load_config("api.config")
        self._logger = self.init_log()
        # self._db = self.init_db()

    @property
    def db(self):
        return self._db

    def init_db(self):

        if self._config['DEBUGMODE']:
            dbecho = True
        else:
            dbecho = False

        db = create_engine(self._config['DATABASE'], echo=dbecho)

        return db

    def test_except(self):
        try:
            mytest = ''
            test = mytest['test_except']
        except Exception as e:
            self._logger.error("Error in test_except %s" % e)
            raise BaseTaskException(e)

    def load_config(self, import_name):
        config = {}
        obj = import_string(import_name)
        for key in dir(obj):
            if key.isupper():
                config[key] = getattr(obj, key)
        return config

    def init_log(self):
        srvlogfile = "{0}/{1}".format(self._config['LOG_PATH'], self._config['TASKS_LOG_FILE'])
        if False and os.path.isfile(srvlogfile):
            try:
                os.remove(srvlogfile)
            except:
                pass

        f = logging.Formatter(fmt='%(levelname)s:%(name)s: %(message)s (%(asctime)s; %(filename)s:%(lineno)d)',
                              datefmt="%Y-%m-%d %H:%M:%S")
        handlers = [
            logging.handlers.RotatingFileHandler(srvlogfile, encoding='utf8', maxBytes=100000, backupCount=1)]

        logger = logging.getLogger('API.TASKS')

        if self._config['DEBUGMODE']:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logger.setLevel(level)

        for h in handlers:
            h.setFormatter(f)
            h.setLevel(level)
            logger.addHandler(h)

        return logger
