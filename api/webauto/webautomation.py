# -*- coding: utf-8 -*-
import time

import lxml.html
from lxml import etree

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import DesiredCapabilities, Remote, ChromeOptions, FirefoxProfile
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options

from api import app
from api.base import ApiBaseException

SELENIUM_HUB = app.config['SELENIUM_HUB']
SELENIUM_DUMP_DIR = app.config['SELENIUM_DUMP_DIR']


class WebAutomatorException(ApiBaseException):
    def __str__(self):
        return repr("Web Automator Error: " + self.message)


class WebAutomator(object):
    _driver = None
    _browsertype = None
    _lxmldoc = None

    def __init__(self, browsertype="Firefox"):
        self._browsertype = browsertype
        service_log_path = app.config['SELENIUM_LOG']

        if self._browsertype == "Firefox":
            self._driver = webdriver.Firefox()
        if self._browsertype == "Chrome":
            self._driver = webdriver.Chrome(app.config['CHROMEDRIVER'])
        elif self._browsertype == "Firefox-Remote":
            profile = FirefoxProfile()
            profile.accept_untrusted_certs = True
            capability = DesiredCapabilities.FIREFOX
            capability['marionette'] = True
            capability["binary"] = app.config['FIREFOX_GECKODRIVER']
            self._driver = Remote(command_executor=SELENIUM_HUB, desired_capabilities=capability)
        elif self._browsertype == "Chrome-Remote":
            options = ChromeOptions()
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            dcap = options.to_capabilities()
            self._driver = Remote(command_executor=SELENIUM_HUB, desired_capabilities=dcap)
        else:
            raise WebAutomatorException("Unknown webdriver selected")

        self.wait = WebDriverWait(self._driver, 10)
        self._driver.set_window_size(1280, 1024)
        #self.driver.set_page_load_timeout(app.config['SELENIUM_TIMEOUT'])

    @property
    def driver(self):
        return self._driver

    @property
    def lxmldoc(self):
        if self._lxmldoc is None:
            try:
                self._lxmldoc = lxml.html.document_fromstring(self._driver.page_source)
            except:
                self._lxmldoc = None
        return self._lxmldoc

    def update_lxmldoc(self):
        self._lxmldoc = lxml.html.document_fromstring(self._driver.page_source)

    def get_element_by_tag_name(self, name):
        try:
            # self.driver.getCurrentWindow()
            elems = self._driver.execute_script("var elems = document.body.getElementsByTagName('%s'); return elems;" % name)
            return elems
        except:
            return None

    def get_element_by_id(self, name):
        try:
            elem = self._driver.find_element_by_id(name)
            return elem
        except:
            return None

    def get_element_by_xpath(self, name):
        try:
            elem = self._driver.find_element_by_xpath(name)
            return elem
        except:
            return None

    def get_elements_by_xpath(self, name):
        try:
            elems = self._driver.find_elements_by_xpath(name)
            return elems
        except:
            elems = None
        return elems

    def get_by_lxml_xpath(self, xpath):
        self.update_lxmldoc()
        try:
            res = self.lxmldoc.xpath(xpath)
        except Exception as e:
            res = None
        return res

    def get_img(self, img_url):
        try:
            path = img_url.split('/')
            file_name = "%s%s" % (app.config['PRODUCT_IMAGE_PATH'], path[-1])
            self.driver.get(img_url)
            img_val = self.driver.get_screenshot_as_file(file_name)
            # self.driver.back()
        except Exception as e:
            print "Error save image %s" %e
            raise ValueError("Error save image %s" %e)

    def documentReadyState(self):
        return self.driver.execute_script("return document.readyState;") == 'complete'

    def close(self):
        time.sleep(4)
        self.driver.quit()
