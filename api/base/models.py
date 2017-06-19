# -*- coding: utf-8 -*-
import re
import json
import datetime
import sqlalchemy as sqla
from sqlalchemy.ext import mutable
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from api import db


class JsonEncodedDict(sqla.TypeDecorator):
  impl = sqla.String

  def process_bind_param(self, value, dialect):
    print ("process_bind_param: ", value)
    return json.dumps(value)

  def process_result_value(self, value, dialect):
    print ("process_result_value: ", value)
    return json.loads(value)

mutable.MutableDict.associate_with(JsonEncodedDict)


def convert_name(name, to_text=False):
    if to_text:
        return re.sub("([a-z])([A-Z])", "\g<1> \g<2>", name)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class BaseMixin(object):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return convert_name(cls.__name__)

    def update(self, data, commit=True):
        for key in data:
            if hasattr(self, key):
                setattr(self, key, data[key])
        if commit:
            db.session.commit()

    def nsave(self, commit=True):
        if commit:
            db.session.commit()

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()

    @classmethod
    def getById(cls, id):
        record = cls.query.filter_by(id=id).first()
        return record

class BaseModel(BaseMixin):
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    update_at = db.Column(db.DateTime, default=datetime.datetime.now())

