# -*- coding: utf-8 -*-
import re
import json

from flask import request, render_template

from api import app, logger
from api.base import BaseTasks, ApiBaseException
from api.tasks import test_tasks, scrapingamazon
from api.models import Scenario, Product
from api.amazonapi.serializers import ScenarioSchema, ProductSchema, ScenarioAsinSchema

remove_space = re.compile("^\s+|\n|\r|\t|\s+$")

@app.route('/')
def api_root():
    try:
        pass
    except Exception as e:
        logger.error(e)
        print e.traceback if hasattr(e, 'traceback') else ''

    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def api_upload():
    logger.debug("Start api_upload...")
    data = {}
    error = False
    errormsg = ''
    try:
        json_data = request.get_json()
        if not json_data:
            raise ApiBaseException('No input data provided')
        asinschema = ScenarioAsinSchema(many=True)
        scenarioschema = ScenarioSchema()
        asins = json_data.get('asins', None)
        if not asins:
            raise ApiBaseException("No input data")
        asins = remove_space.sub('', asins)
        asins = asins.split(";")
        print asins
        if len(asins) == 0:
            raise ApiBaseException("No input data")
        scenario = Scenario({'data':asins})
        scenario.save()
        if scenario:
            celerytask = scrapingamazon.delay(scenario.id)
#            celerytask = scrapingamazon.apply_async([scenario.id])
            print "celerytask:", celerytask
            #celerytask = 'celeryID'
            if not celerytask:
                raise ApiBaseException(scenario.errormsg)
            scenario.update({'celerytask':str(celerytask)})
            data = scenarioschema.dump(scenario).data
        else:
            error = 1
            errormsg = "Can't save scanario"
    except Exception as e:
        error = 1
        print "api_upload error %s" % e
        errormsg = "api_upload error %s" % e
        logger.error(errormsg)
        logger.error(e.traceback) if hasattr(e, 'traceback') else ''

    result = {'error': error, 'errormsg': errormsg, 'scenario': data}
    return (json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'})

@app.route('/lastscenario', methods=['GET'])
def api_get_scenarios():
    logger.debug("Start api_get_scenarios...")
    error = False
    errormsg = ''
    data = []

    try:
        scenario = Scenario.query.order_by(Scenario.id.desc()).limit(10).all()
        if not scenario:
            raise ApiBaseException("Can't find scenario# %s" % id)
        scenarioschema = ScenarioSchema(many=True)
        data = scenarioschema.dump(scenario).data
    except Exception as e:
        error = True
        errormsg = "api_upload error %s" % e
        logger.error(errormsg)
        print errormsg
        print (e.traceback) if hasattr(e, 'traceback') else ''

    result = {'error': error, 'errormsg': errormsg, 'scenarios': data}
    return (json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'})


@app.route('/products', methods=['GET'])
def api_get_products():
    error = False
    errormsg = ''
    data = []
    try:
        products = Product.query.all()
        if not products:
            raise ApiBaseException("Can't find scenario# %s" %id)

        return render_template('products.html', products=products)

    except Exception as e:
        error = True
        errormsg = "api_upload error %s" % e
        logger.error(errormsg)
        print errormsg
        print (e.traceback) if hasattr(e, 'traceback') else ''


    result = {'error': error, 'errormsg': errormsg, 'scenario': data}
    return (json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'})

@app.route('/scenario/<id>', methods=['GET'])
def api_get_scenario(id):
    logger.debug("Start api_get_scenario...")
    error = False
    errormsg = ''
    data = []
    try:
        scenario = Scenario.getById(id)
        products = Product.query.filter_by(scenario_id=id).all()
        if not scenario:
            raise ApiBaseException("Can't find scenario# %s" %id)
        scenarioamazon = ScenarioSchema()
        productsscenario = ProductSchema(many=True)
        scenarioamazon = scenarioamazon.dump(scenario).data
        products = productsscenario.dump(products).data
        data = {'scenario': scenarioamazon, 'products': products}
    except Exception as e:
        error = True
        errormsg = "api_upload error %s" % e
        logger.error(errormsg)
        print errormsg
        print (e.traceback) if hasattr(e, 'traceback') else ''

    result = {'error': error, 'errormsg': errormsg, 'scenario': data}
    return (json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'})
