from marshmallow import Schema, fields
import datetime
import time

class AsinSchema(Schema):
    asin = fields.Str()

class ScenarioAsinSchema(Schema):
    asins = fields.Nested(AsinSchema, many=True)

class BaseScenarioSchema(Schema):
    id = fields.Integer()
    created_at = fields.DateTime(format="%Y-%m-%d")
    update_at = fields.DateTime(format="%Y-%m-%d")

class ProductSchema(BaseScenarioSchema):
    scenario_id = fields.Integer()
    asin = fields.Str()
    title = fields.Str()
    description = fields.Str()
    url = fields.Str()
    price = fields.Float()
    photos = fields.Dict()
    other = fields.Dict()
    status = fields.Str()
    ebay_update = fields.Boolean()

class ScenarioSchema(BaseScenarioSchema):
    asins = fields.Dict()
    asins_scraping = fields.Dict()
    asins_error = fields.Dict()
    celerytask = fields.Str()
    status = fields.Str()
