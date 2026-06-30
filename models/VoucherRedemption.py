from datetime import datetime
from extensions import db

class VoucherRedemption(db.Model):
    __tablename__ = 'voucher_redemption'
    id = db.Column(db.Integer, primary_key=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey('voucher.id', ondelete='CASCADE'), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    voucher = db.relationship('Voucher', backref=db.backref('redemptions', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return '<VoucherRedemption %r - %r>' % (self.voucher_id, self.phone_number)
