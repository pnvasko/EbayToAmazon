# -*- coding: utf-8 -*-
import os
import logging
import logging.handlers
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

__all__ = ["create_app", "make_celery"]

class App(Flask):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.config.from_object('api.config')
        self._logger = self.init_log()
        self.init_sql_db()

    @property
    def db(self):
        return self._sql_db

    def init_sql_db(self):
        self._sql_db = SQLAlchemy(self)

    @property
    def logger(self):
        return self._logger

    def init_log(self):
        srvlogfile = "{0}/{1}".format(self.config['LOG_PATH'], self.config['WEB_LOG_FILE'] )
        if False and os.path.isfile(srvlogfile):
            try:
                os.remove(srvlogfile)
            except:
                pass

        f = logging.Formatter(fmt='%(levelname)s:%(name)s: %(message)s (%(asctime)s; %(filename)s:%(lineno)d)',
                              datefmt="%Y-%m-%d %H:%M:%S")
        handlers = [
            logging.handlers.RotatingFileHandler(srvlogfile, encoding='utf8', maxBytes=100000, backupCount=1)]

        logger = logging.getLogger('API.WEB')

        if self.config['DEBUG']:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logger.setLevel(level)

        for h in handlers:
            h.setFormatter(f)
            h.setLevel(level)
            logger.addHandler(h)

        return logger

def create_app():
    app = App(__name__)
    Bootstrap(app)
    return app

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery