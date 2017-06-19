# -*- coding: utf-8 -*-
import re
import time
import logging
import lxml.html
from lxml import etree
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

#from celery import task
from celery.utils.log import get_logger

from api import app, celery
from api.models import Scenario, Product, EbayProduct
from api.base import BaseTasks, ApiBaseException
from api.ebayapi import BaseEbaiAPI
from api.webauto import WebAutomator

remove_space = re.compile("^\s+|\n|\r|\t|\s+$")
delimiter_change = re.compile("\s\s+|\t+")
idfind = re.compile("^\d+$")
testcondition = re.compile("([=<>]*)\s*[\'\"](.*)[\'\"]")
selectcondition = re.compile("^(.+):[\'\"](.+)[\'\"]$")
classsplit = re.compile('\s+')
node_filter = re.compile('node=(\d+)')
price_filter = re.compile('\w+(\d+[\,\.]*\d*)')
remove_w_space = re.compile("\s+")
availability_filter = re.compile('en stock')
free_shipping_filter = re.compile('livraison gratuite')

def removespace(text):
    if text and (isinstance(text,str) or isinstance(text,unicode)):
        cleartext = remove_space.sub('', text)
        return cleartext
    else:
        return text

def stringify_children(node):
    from lxml.etree import tostring
    from itertools import chain
    print "stringify_children: ", node
    print "stringify_children text: ", node.text
    parts = ([node.text] +
            list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
            [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))

def get_attrib(elem, name):
    try:
        return elem.attrib[name]
    except:
        return None

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

class ScenarioProductScraping(BaseTasks):
    error = False
    errormsg = ''
    url_login = "https://www.amazon.fr/"
    url = "https://www.amazon.fr/gp/product/%s/ref=oh_aui_detailpage_o02_s00?ie=UTF8&amp;psc=1"

    def __init__(self, id):
        super(ScenarioProductScraping, self).__init__()
        self.lxmldoc = None
        self.scenario = Scenario.getById(id)

    def start(self):
        asin = None
        asins_scraping = []
        asins_error = []
        status = ''
        try:
            asins = self.scenario.asins['data']
        except:
            asins = None
        if not asins or len(asins) == 0:
            self.scenario.update({'status': 'ERROR'})
            self.error = True
            self.errormsg = "Can't find asin for scraping"
            raise ApiBaseException(self.errormsg)

        client = WebAutomator(browsertype=app.config['SELENIUM_BROWSER'])
        # Start login to amazon.fr
        client.driver.get(self.url_login)
        login = client.get_element_by_xpath(".//*[@id='nav-link-yourAccount']")
        if login:
            try:
                login.click()
                ""
                client.wait.until(lambda ready: client.documentReadyState())
                client.wait.until(lambda ready: client.get_by_lxml_xpath(".//*[@id='ap_email']"))
                ap_email = client.get_element_by_xpath(".//*[@id='ap_email']")
                ap_password = client.get_element_by_xpath(".//*[@id='ap_password']")
                signInSubmit = client.get_element_by_xpath(".//*[@id='signInSubmit']")
                ap_email.send_keys(app.config['AMAZON_USERNAME'])
                time.sleep(0.5)
                ap_password.send_keys(app.config['AMAZON_PASSWORD'])
                time.sleep(0.5)
                signInSubmit.click()

            except Exception as e:
                print "ERROR:", e

                self.scenario.update({'status': "ERROR LOGIN"})
                raise ApiBaseException("ERROR LOGIN")
        else:
            self.scenario.update({'status': "ERROR LOGIN"})
        path = "%s/%s.png" % (app.config['SELENIUM_DUMP_DIR'], 'login.png')
        client.driver.save_screenshot(path)
        #Finish login to amazon.fr
        self.scenario.update({'status': "START"})
        try:
            asin_count = len(asins)
            i = 0
            for asin in asins:
                if asin is None or asin == '':
                    continue
                try:
                    logger.debug('Scenario start get page source for asin: %s' % asin)
                    i += 1
                    self.scenario.update({'status': "START. %s at %s" % (i, asin_count)})
                    product = Product.getByTaskAsin(asin)
                    if not product:
                        product = Product(asin, self.scenario.id)
                        product.save()
                    else:
                        pass
                        #continue
                        # TODO exist asin

                    url = self.url % asin
                    client.driver.get(url)
                    client.wait.until(lambda ready: client.documentReadyState())
                    client.wait.until(lambda ready: client.get_by_lxml_xpath(".//*/input[@id='ASIN' or @id='asin']"))
                    asin_input = client.get_by_lxml_xpath(".//*/input[@id='ASIN' or @id='asin']")
                    if not asin_input:
                        product.update({'status': 'ERROR', 'error': "Can't get amazon page for asin: %s" % asin})
                        path = "%s/%s.png" % (app.config['SELENIUM_DUMP_DIR'], asin)
                        client.driver.save_screenshot(path)
                        raise ApiBaseException("Can't get amazon page for asin: %s" % asin)

                    client.update_lxmldoc()

                    productTitle = client.get_by_lxml_xpath(".//*[@id='productTitle']/text()")
                    if productTitle:
                        productTitle = productTitle[0]
                    productTitle = removespace(productTitle)

                    productDescription = client.get_by_lxml_xpath(".//*[@id='productDescription']")
                    if productDescription:
                        productDescription = ''.join(productDescription[0].itertext()).strip()
                    productDescription = removespace(productDescription)

                    categories = client.get_by_lxml_xpath(".//*[@id='wayfinding-breadcrumbs_feature_div']/.//a")
                    categorie_list = []
                    categorie_node = {}
                    if categories:
                        for categorie in categories:
                            # logger.info("categorie: %s" % removespace(categorie.text))
                            node = get_attrib(categorie, 'href')
                            if node is not None:
                                node = node_filter.search(node)
                                if node is not None:
                                    node = node.group(1)
                            categorie_text = removespace(categorie.text)
                            categorie_list.append(categorie_text)
                            categorie_node[categorie_text] = node

                    priceBlockOurprice = client.get_by_lxml_xpath(".//*[@id='priceblock_ourprice']/text()")
                    if priceBlockOurprice:
                        priceBlockOurprice = priceBlockOurprice[0]
                        priceBlockOurprice = removespace(priceBlockOurprice)
                        priceBlockOurprice = price_filter.search(priceBlockOurprice)
                        if priceBlockOurprice:
                            priceBlockOurprice = priceBlockOurprice.group(0)
                            priceBlockOurprice = '.'.join(priceBlockOurprice.split(','))
                            priceBlockOurprice = float(priceBlockOurprice)
                    else:
                        priceBlockOurprice = None

                    productAvailability = client.get_by_lxml_xpath(".//div[@id='availability']/span/text()")
                    if productAvailability:
                        productAvailability = productAvailability[0]
                        productAvailability = removespace(productAvailability)
                        if productAvailability == "En stock.":
                            productAvailability = True
                        elif availability_filter.search(remove_w_space.sub(' ',remove_space.sub('', productAvailability.lower()))):
                            productAvailability = True
                        else:
                            productAvailability = False
                    else:
                        productAvailability = False

                    if not productAvailability:
                        productAvailability = client.get_by_lxml_xpath(".//input[@id='add-to-cart-button']")
                        if productAvailability:
                            productAvailability = True
                        else:
                            productAvailability = False

                    productPremium = client.get_elements_by_xpath(".//span[@id='priceBadging_feature_div']/i[contains(@class, 'a-icon-premium')]")
                    if productPremium:
                        productPremium = True
                    else:
                        try:
                            productPremium = client.get_by_lxml_xpath(".//div[@id='priceBadging_feature_div']")
                            if productPremium:
                                productPremium = ''.join(productPremium[0].itertext()).strip()
                                if free_shipping_filter.search(productPremium.lower()):
                                    productPremium = True
                                else:
                                    productPremium = False
                            else:
                                productPremium = False
                        except:
                            productPremium = False


                    prodDetails = client.get_by_lxml_xpath(".//div[@id='prodDetails']/.//div[contains(@class, 'col1')]/.//table/tbody/tr")
                    productDetails = []
                    if prodDetails:
                        for tr in prodDetails:
                            try:
                                td0 = removespace(tr[0].text)
                                td1 = removespace(tr[1].text)
                                if len(td0) > 1 and len(td0) > 1:
                                    productDetails.append((td0, td1))
                            except:
                                pass

                    productPhotos = {}
                    photos = client.get_elements_by_xpath(".//div[@id='altImages']/.//span[contains(@id,'a-autoid-') and contains(@class, 'a-button-thumbnail')]")
                    if photos is not None:
                        for photo in photos:
                            try:
                                photo.click()
                                time.sleep(.5)
                            except Exception as e:
                                pass

                    client.update_lxmldoc()
                    imgTagWrapper = client.get_by_lxml_xpath(".//*[@class='imgTagWrapper']/img")
                    photo_img = None
                    try:
                        if imgTagWrapper:
                            for imgTag in imgTagWrapper:
                                photo_img = get_attrib(imgTag, 'src')
                                if photo_img is not None:
                                    productPhotos[photo_img] = 1
                            for photo_img in productPhotos:
                                client.get_img(photo_img)
                    except Exception as e:
                        logger.error('Scenario start can\'t get image for asin: %s, url: %s. %s' % (asin, photo_img, e))

                    other = {'categorielist': categorie_list,
                             'categorie_node':categorie_node,
                             'product_details': productDetails,
                             'product_premium': productPremium,
                             'product_availability': productAvailability
                             }


                    status = 'Not start'

                    product_data = { 'title': productTitle,
                                     'description': productDescription,
                                     'url': url,
                                     'price': priceBlockOurprice,
                                     'photos': productPhotos,
                                     'other': other,
                                     'status': status,
                                     'ebay_update': False
                                     }


                    if not (asin and productTitle and priceBlockOurprice and productAvailability and productPremium):
                        client.driver.get(url)
                        erro_filds = []
                        if not asin:
                            erro_filds.append('Asin')
                        if not productTitle:
                            erro_filds.append('Title')
                        if not priceBlockOurprice:
                            erro_filds.append('Price')
                        if not productAvailability:
                            erro_filds.append('Not stock')
                        if not productPremium:
                            erro_filds.append('Not premium')

                        raise ApiBaseException("Can't get: %s" % (";".join(erro_filds)))

                    product.update(product_data)
                    asins_scraping.append(asin)

                except Exception as e:
                    logger.error("Error ScenarioProductScraping start; asin next: %s" % e)
                    if product:
                        product.update({'status': 'ERROR', 'error': "Can't get amazon page for asin: %s, error: %s" % (asin, e)})
                    path = "%s/%s.png" % (app.config['SELENIUM_DUMP_DIR'], asin)
                    client.driver.save_screenshot(path)
                    asins_error.append(asin)
                status = 'DONE'
        except Exception as e:
            self.error = True
            status = "ERROR. Asin: %s" % asin
            self.errormsg = "Can't make scraping %s" % e
            raise ApiBaseException(self.errormsg)
        finally:
            self.scenario.update({'status': status,
                                  'asins_scraping': {'data':asins_scraping},
                                  'asins_error': {'data': asins_error }})
            try:
                client.close()
            except:
                logger.error('Error ScenarioProductScraping finish selenium automator')

class EbayAddProduct(BaseTasks):
    error = False
    errormsg = ''

    def __init__(self, id):
        logger.debug('EbayAddProduct init')
        super(EbayAddProduct, self).__init__()
        self._ebay = BaseEbaiAPI(app)
        self.scenario = Scenario.getById(id)

    def add_product(self, asin):
        logger.debug('EbayAddProduct add_product start')
        product = Product.getByTaskAsin(asin)
        if product.ebay_update:
            return True

        response = self._ebay.add_product(product)
        item = response.item
        error = response.error
        errormsg = response.errormsg
        errordict = response.errordict

        if not error:
            res = response.resp.dict()
            itemid = res['ItemID']

            ebay_product = EbayProduct(itemid, product.id)
            ebay_product.price = item['Item']['StartPrice']
            ebay_product.item = item
            ebay_product.error = errordict
            ebay_product.status = "ADDEBAY"
            ebay_product.save()

            product.update({'ebay_update':True,
                            'status': 'ADDEBAY',
                            'error': '',
                            'ebay_update_error': errordict}
                           )
            return True
        else:
            product.update({'ebay_update':False,
                            'status': 'ERROR',
                            'error': errormsg,
                            'ebay_update_error': errordict})
            return False

    def start(self):
        logger.debug('EbayAddProduct start ...')
        products_add = []
        products_error = []
        if self.scenario.asins_scraping:
            asins = self.scenario.asins_scraping['data']
            for asin in asins:
                res = self.add_product(asin)
                if res:
                    products_add.append(asin)
                else:
                    products_error.append(asin)
            self.scenario.update({'asins_ebay':{'add': products_add, 'error': products_error}})

@celery.task(bind=True)
def test_tasks(*args, **kwargs):
    print ("print test_tasks {0}, {1}".format(args, kwargs))
    logger.info("test_tasks {0}, {1}".format(args, kwargs))
    x = 100 + 100
    logger.info("test_tasks end: {0}".format(x))
    return x

@celery.task
def scrapingamazon(id):
    logger.debug("scrapingamazon start")
    try:
        product_scraping = ScenarioProductScraping(id)
        product_scraping.start()
        product_scraping = None
        ebay_add_master = EbayAddProduct(id)
        ebay_add_master.start()
        ebay_add_master = None
    except Exception as e:
        logger.error("Error in scrapingamazon: %s" % e)

class ScenarioException(ApiBaseException):
    def __str__(self):
        return 'Task error: {0}'.format(self.message)
