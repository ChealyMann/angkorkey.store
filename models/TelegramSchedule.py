from datetime import datetime
from extensions import db

class TelegramSchedule(db.Model):
    __tablename__ = 'telegram_schedule'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', name='fk_telegram_schedule_product_id_product'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    caption = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False) # pending, sent, failed
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    images_json = db.Column(db.Text, nullable=True) # JSON string representation of list of images

    product = db.relationship('Product', backref='schedules', lazy=True)

    def __repr__(self):
        return f'<TelegramSchedule Product:{self.product_id} Time:{self.scheduled_time} Status:{self.status}>'
