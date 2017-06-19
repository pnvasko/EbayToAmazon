from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from ebaysdk.finding import Connection as Finding

class BaseEbaiAPIResponse(object):
    def __init__(self, resp=None, item=None, error=False, errormsg='', errordict=None):
        self.resp = resp
        self.item = item
        self.error = error
        self.errormsg = errormsg
        self.errordict = errordict

    def __repr__(self):
        return "%s, Error: <%s>" % (self.resp, self.error)


class BaseEbaiAPI(object):
    def __init__(self, app):
        super(BaseEbaiAPI, self).__init__()
        self._logger = app.logger
        self._config = app.config

        if self._config['EBAY_MODE'] == 'Sandbox':
            self.config = self._config['EBAY_CONFIG']['SANDBOX']
        else:
            self.config = self._config['EBAY_CONFIG']['PRODACTION']

        self._ebay_trading_api = Trading(domain = self.config['EBAY_DOMAIN'],
                                         siteid = self.config['EBAY_SITEID'],
                                         appid = self.config['EBAY_APPID'],
                                         devid = self.config['EBAY_DEVID'],
                                         certid = self.config['EBAY_CERTID'],
                                         token = self.config['EBAY_TOKEN'],
                                         compatibility = self.config['EBAY_COMPATABILITY'],
                                         config_file = None
                                 )

    @property
    def trading(self):
        return self._ebay_trading_api

    def trading_execute(self, func, query):
        return self._ebay_trading_api.execute(func, query)

    def make_item_price(self, price):
        if price > 0 and price < self.config['EBAY_HI_PRICE']:
            ebay_price = price * self.config['EBAY_LOW_PRICE_MOD']
        else:
            ebay_price = price * self.config['EBAY_HI_PRICE_MOD']

        return ebay_price

    def make_item_title(self, title):
        if len(title) > 80:
            titles = ' '.split(title)
            if len(titles) == 1:
                return title[0:79]
            len_title = 0
            out = ''
            for w in titles:
                len_title = len_title + len(w)
                if len_title < 80:
                    out = "%s %s" %(out, w)
                else:
                    break
            return out
        else:
            return title

    def make_item(self, product):
        category = self.get_category_by_product_name(product.title)
        if category:
            CategoryID = category.CategoryID
        else:
            CategoryID = self.config['EBAY_DEFUALT_CATEGORY']
        StartPrice = self.make_item_price(product.price)
        PictureUrls = []
        if product.photos:
            for url in product.photos:
                PictureUrls.append(url)

        item = {
            "Item": {
                "Title": self.make_item_title(product.title),
                "Description": product.description,
                "PrimaryCategory": {"CategoryID": "%s" % CategoryID},
                "StartPrice": "%s" % StartPrice,
                "CategoryMappingAllowed": "true",
                "Country": self.config['EBAY_COUNTRY'],
                "ConditionID": "1000",
                "Currency": self.config['EBAY_CURRENCY'],
                "DispatchTimeMax": "3",
                "ListingDuration": "Days_7",
                "ListingType": "FixedPriceItem",
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": self.config['EBAY_PAYPAL_EMAIL'],
                "PictureDetails": {"PictureURL": PictureUrls},
                "PostalCode": self.config['EBAY_POSTAL_CODE'],
                "Quantity": "1",
                "ProductListingDetails": {
                    'EAN': 'Does not apply',
                    'BrandMPN':{
                        'Brand': 'Does not apply',
                        'MPN': 'Does not apply',
                    }
                },
                "ItemSpecifics": {
                    "NameValueList": [
                        {"Name": "Brand", "Value": "Does not apply"},
                        {"Name": "MPN", "Value": "Does not apply"},
                    ]
                },
                "ReturnPolicy": {
                    "ReturnsAcceptedOption": "ReturnsAccepted",
                    "RefundOption": "MoneyBack",
                    "ReturnsWithinOption": "Days_30",
                    "Description": "If you are not satisfied, return the good for refund.",
                    "ShippingCostPaidByOption": "Buyer"
                },
                "ShippingDetails": {
                    "ShippingType": "Flat",
                    "ShippingServiceOptions": {
                        "ShippingServicePriority": "1",
                        "ShippingService": self.config['EBAY_SHIPPING_SERVICE'],
                        "ShippingServiceCost": "0"
                    }
                },
                "Site": self.config['EBAY_SITE']
            }
        }

        return item

    def verify_add_product(self, product):
        print "Start verify_add_product"
        error = False
        errormsg = ''
        errordict = None
        result = {}
        item = {}
        try:
            item = self.make_item(product)
            result = self._ebay_trading_api.execute('VerifyAddItem', item)
        except ConnectionError as e:
            error = True
            errormsg = '%s' % e
            errordict = e.response.dict()
            self._logger.error("verify_add_product ConnectionError: %s" % errormsg)
        except Exception as e:
            error = True
            errormsg = '%s' % e
            self._logger.error("verify_add_product error: %s" % errormsg)
        response = BaseEbaiAPIResponse(resp=result, item = item,
                                       error=error, errormsg=errormsg, errordict=errordict)
        return response

    def add_product(self, product):
        error = False
        errormsg = ''
        errordict = None
        result = {}
        item = {}

        try:
            item = self.make_item(product)
            result = self._ebay_trading_api.execute('AddItem', item)
        except ConnectionError as e:
            error = True
            errormsg = '%s' % e
            errordict = e.response.dict()
            self._logger.error("add_product ConnectionError: %s" % errormsg)
        except Exception as e:
            error = True
            errormsg = '%s' % e
            self._logger.error("add_product error: %s" % errormsg)

        response = BaseEbaiAPIResponse(resp=result, item = item,
                                       error=error, errormsg=errormsg, errordict=errordict)
        return response

    def get_category_by_product_name(self, product_name):
        category = None
        try:
            product_key = product_name.split(" ")
            product_key = " ".join(product_key[0: 5])
            query = {'Query': product_key}
            config = self._config['EBAY_CONFIG']['PRODACTION']
            api = Trading(domain=config['EBAY_DOMAIN'],
                                         siteid=config['EBAY_SITEID'],
                                         appid=config['EBAY_APPID'],
                                         devid=config['EBAY_DEVID'],
                                         certid=config['EBAY_CERTID'],
                                         token=config['EBAY_TOKEN'],
                                         compatibility=config['EBAY_COMPATABILITY'],
                                         config_file=None
                                         )
            response = api.execute('GetSuggestedCategories', query)
            if int(response.reply.CategoryCount) > 0:
                category = response.reply.SuggestedCategoryArray.SuggestedCategory[0].Category
        except Exception as e:
            print "Error:", e
            self._logger.error("get_category_by_product_name error: %s" % e)

        return category