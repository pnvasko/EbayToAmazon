# -*- coding: utf-8 -*-
import os

DEBUGMODE = False
DEBUG = True

CSRF_ENABLED = True
WTF_CSRF_ENABLED = False
THREADS_PER_PAGE = 2
CSRF_SESSION_KEY = "--------------you key here--------------"
WTF_CSRF_SECRET_KEY = '--------------you key here--------------'
SECRET_KEY = '--------------you key here--------------'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgres://--------------you DB here--------------'

CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_ENABLE_UTC = True

# --------------------------------------------------
if False:
    CELERY_BROKER = "redis://localhost:6379"
    CELERY_BROKER_URL = "redis://localhost:6379"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    CELERY_TASK_RESULT_EXPIRES = 3600
else:
    BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    CELERY_BROKER  = 'amqp://guest:guest@localhost:5672//'
    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'

    CELERYD_MAX_TASKS_PER_CHILD = 1
    CELERY_DEFAULT_QUEUE = 'celery'

AMAZON_USERNAME = '--------------you amazon username --------------'
AMAZON_PASSWORD = '--------------you amazon passwrod --------------'

# EBAY_MODE = 'Sandbox'
EBAY_MODE = 'Prodaction'
EBAY_CONFIG = {
    'SANDBOX':{
        'EBAY_DOMAIN'       : 'api.sandbox.ebay.com',
        'EBAY_SITEID'       : '1',
        'EBAY_APPID'        : '--------------you Ebay API key --------------',
        'EBAY_CERTID'       : '--------------you Ebay API cert --------------',
        'EBAY_DEVID'        : '--------------you Ebay dev key --------------',
        'EBAY_TOKEN'        : '--------------you Ebay token --------------',
        'EBAY_COMPATABILITY': '719',
        'EBAY_SITE'         : 'US',
        'EBAY_COUNTRY'      : 'US',
        'EBAY_CURRENCY'     : 'USD',
        'EBAY_PAYPAL_EMAIL' : '--------------you paypal for ebay --------------',
        'EBAY_POSTAL_CODE'  : '75009',
        'EBAY_SHIPPING_SERVICE' : 'USPSMedia',
        'EBAY_DEFUALT_CATEGORY' : '31770',
        'EBAY_HI_PRICE'      : 15,
        'EBAY_HI_PRICE_MOD'  : 1.33,
        'EBAY_LOW_PRICE_MOD' :1.5
    },
    'PRODACTION':{
        'EBAY_DOMAIN'       : 'api.ebay.com',
        'EBAY_SITEID'       : '71',
        'EBAY_APPID'        : '--------------you Ebay API key --------------',
        'EBAY_CERTID'       : '--------------you Ebay API cert --------------',
        'EBAY_DEVID'        : '--------------you Ebay dev key --------------',
        'EBAY_TOKEN'        : '--------------you Ebay token --------------',
        'EBAY_COMPATABILITY': '719',
        'EBAY_SITE'         : 'France',
        'EBAY_COUNTRY'      : 'FR',
        'EBAY_CURRENCY'     : 'EUR',
        'EBAY_PAYPAL_EMAIL' : '--------------you paypal for ebay --------------',
        'EBAY_POSTAL_CODE'  : '75009',
        'EBAY_SHIPPING_SERVICE': 'FR_ColiposteColissimo',
        'EBAY_DEFUALT_CATEGORY': '31770',
        'EBAY_HI_PRICE': 15,
        'EBAY_HI_PRICE_MOD': 1.33,
        'EBAY_LOW_PRICE_MOD': 1.5
    }
}

SELENIUM_BROWSER = 'Chrome-Remote'
SELENIUM_HUB = "http://localhost:4444/wd/hub"
SELENIUM_TIMEOUT = 30

SELENIUM_LOG = 'logs/selenium.log'
SELENIUM_DUMP_DIR = 'logs/dump'

CHROMEDRIVER = 'env/bin/chromedriver'
FIREFOX_GECKODRIVER = "env/bin/geckodriver"

PRODUCT_IMAGE_PATH = 'img/products/'
LOG_PATH = 'logs/'
WEB_LOG_FILE = 'web_app_server.log'
CELERY_LOG_FILE = 'celery_app_server.log'
TASKS_LOG_FILE = 'tasks.log'
