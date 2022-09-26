from flask_marshmallow import Marshmallow
from marshmallow import validate


ma = Marshmallow()


class UserSchema(ma.Schema):
    password = ma.Str(required=True, validate=[
                      validate.Length(min=8, max=12)])


class ReagentSchema(ma.Schema):
    id = ma.Str(required=True, validate=[
        validate.Length(max=9)])
    name = ma.Str(required=True, validate=[
        validate.Length(max=10)])
