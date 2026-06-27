from flask import abort, redirect

from extensions import db
from sqlalchemy.sql import text
class Brand(db.Model):
    __tablename__ = 'brand'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),unique = True,nullable = False)
    desc = db.Column(db.String(255))
    image = db.Column(db.String(255))
    status = db.Column(db.String(5), nullable = False)

    def __repr__(self):
        return '<Brand %r>' % self.name


