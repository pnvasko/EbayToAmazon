# -*- coding: utf-8 -*-
import json
from flask import request, render_template
from api import app, logger
from api.base import ApiBaseException
from api.models import Product
from base import BaseEbaiAPI

@app.route('/ebaytest')
def api_ebay_index():
    return render_template('ebayapi.html')

@app.route('/ebaytest/additem/<asin>', methods=['GET'])
def api_ebaytest_additem(asin):
    logger.debug("Start api_ebaytest_finditem...")
    error = False
    errormsg = ''
    res = {}
    try:
        ebay = BaseEbaiAPI(app)
        # http://developer.ebay.com/devzone/xml/docs/Reference/eBay/AddItem.html
        # https://gist.github.com/davidtsadler/4581805
        product = Product.getByTaskAsin(asin)
        print "verify_add_product start"
        response = ebay.verify_add_product(product)
        print "verify_add_product finish"
        if not response.error:
            print "Can add"
            # response = ebay.add_product(product)

        print "--------------------------------------------------------------"
        print "resp: ", response.resp
        print "--------------------------------------------------------------"
        print "error: ", response.error
        print "--------------------------------------------------------------"
        print "errormsg: ", response.errormsg
        print "--------------------------------------------------------------"
        print "errordict: ", response.errordict
        print "--------------------------------------------------------------"
        error = response.error
        errormsg = response.errormsg
        if not response.error:
            res = response.resp.dict()
            res = res['ItemID']
    except Exception as e:
        error = True
        errormsg = "api_upload error %s" % e
        logger.error(errormsg)
        print errormsg
        print (e.traceback) if hasattr(e, 'traceback') else ''

    result = {'error': error, 'errormsg': errormsg, 'item': res}
    return (json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'})


@app.route('/ebaytest/finditem', methods=['GET'])
def api_ebaytest_finditem():
    logger.debug("Start api_ebaytest_finditem...")
    error = False
    errormsg = ''
    category = {}
    try:
        ebay = BaseEbaiAPI(app)
        product_name = "Oral-B Vitality Sensitive Clean Brosse à Dents Electrique Rechargeable, par Braun"
        category = ebay.get_category_by_product_name(product_name)
        category = "%s" % category
    except Exception as e:
        error = True
        errormsg = "api_upload error %s" % e
        logger.error(errormsg)
        print errormsg
        print (e.traceback) if hasattr(e, 'traceback') else ''

    result = {'error': error, 'errormsg': errormsg, 'category': category}
    return (json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'})

@app.route('/ebaytest/getuser', methods=['GET'])
def api_ebaytest_getuser():
    logger.debug("Start api_ebaytest_getuser...")
    error = False
    errormsg = ''
    data = []
    try:
        ebay = BaseEbaiAPI(app)
        response = ebay.trading_execute('GetUser', {})
        data = response.dict()
    except Exception as e:
        error = True
        errormsg = "api_upload error %s" % e
        logger.error(errormsg)
        print errormsg
        print (e.traceback) if hasattr(e, 'traceback') else ''

    result = {'error': error, 'errormsg': errormsg, 'data': data}
    return (json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'})