# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSON

from api import db
from api.base import BaseModel


class Scenario(BaseModel, db.Model):
    asins = db.Column(JSON, nullable=True)
    asins_scraping = db.Column(JSON, nullable=True)
    asins_error = db.Column(JSON, nullable=True)
    asins_ebay = db.Column(JSON, nullable=True)
    celerytask = db.Column(db.String(254), nullable=True)
    status = db.Column(db.String(64), nullable=True)

    def __init__(self, asins):
        self.status = "Not start"
        self.asins = asins

    @classmethod
    def getById(cls, id):
        scenario = cls.query.filter_by(id=id).first()
        return scenario

    def asins_error_update(self, asin):
        if (self.asins_error is None):
            asins_error = []
        else:
            if 'data' not in self.asins_error:
                asins_error = []
            else:
                asins_error = self.asins_error['data']
        asins_error.append(asin)
        self.update({'asins_error': {'data': asins_error}})

    def asins_scraping_update(self, asin):
        if (self.asins_scraping is None):
            asins_scraping = []
        else:
            if 'data' not in self.asins_scraping:
                asins_scraping = []
            else:
                asins_scraping = self.asins_scraping['data']
        asins_scraping.append(asin)
        self.update({'asins_scraping': {'data': asins_scraping}})

    def __repr__(self):
        return "%s at %s" % (self.id, self.created_at)


class Product(BaseModel, db.Model):
    asin = db.Column(db.String(254), unique=True, nullable=False)
    title = db.Column(db.String(254), nullable=True)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(254), nullable=True)
    price = db.Column(db.Float, default=0)
    photos = db.Column(JSON)
    other = db.Column(JSON)
    error = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(10), nullable=True)

    ebay_update_error = db.Column(JSON)
    ebay_update = db.Column(db.Boolean)

    scenario_id = db.Column(db.Integer, ForeignKey('scenario.id'), nullable=False)
    scenario = relationship(Scenario, foreign_keys=[scenario_id], backref=backref("products"))

    def __init__(self, asin, scenario_id):
        self.asin = asin
        self.scenario_id = scenario_id

    @classmethod
    def getByTaskId(cls, id):
        product = cls.query.filter_by(id=id).first()
        return product

    @classmethod
    def getByTaskAsin(cls, asin):
        product = cls.query.filter_by(asin=asin).first()
        return product

    def __repr__(self):
        return "%s <%s>" % (self.id, self.asin)


class EbayProduct(BaseModel, db.Model):
    itemid = db.Column(db.String(60), unique=True, nullable=False)
    price = db.Column(db.Float, default=0)
    item = db.Column(JSON)
    error = db.Column(JSON)
    status = db.Column(db.String(64), nullable=True)

    amazonproduct_id = db.Column(db.Integer, ForeignKey('product.id'), nullable=False)
    amazonproduct = relationship(Product, foreign_keys=[amazonproduct_id], backref=backref("ebayproduct"))


    def __init__(self, itemid, amazonproduct_id):
        self.itemid = itemid
        self.amazonproduct_id = amazonproduct_id

    @classmethod
    def getById(cls, id):
        product = cls.query.filter_by(id=id).first()
        return product

    @classmethod
    def getByItemID(cls, itemid):
        product = cls.query.filter_by(itemid=itemid).first()
        return product


    def __repr__(self):
        return "%s <%s>" % (self.id, self.itemid)