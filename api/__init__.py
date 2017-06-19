# -*- coding: utf-8 -*-
from app import create_app, make_celery

__all__ = [
    'app',
    'logger',
    'db'
]

app = create_app()
logger = app.logger
db = app.db

app.debug = True
logger.debug('Start api init...')

celery = make_celery(app)

import api.amazonapi.view
import api.ebayapi.view
