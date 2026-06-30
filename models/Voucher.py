from extensions import db

class Voucher(db.Model):
    __tablename__ = 'voucher'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    min_spend = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(5), nullable=False, default='true')
    usage_limit = db.Column(db.Integer, nullable=True)  # Null means unlimited
    usage_count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<Voucher %r>' % self.code
