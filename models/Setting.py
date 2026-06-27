from extensions import db

class Setting(db.Model):
    __tablename__ = 'setting'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    @staticmethod
    def get_val(key, default=None):
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set_val(key, val):
        setting = Setting.query.filter_by(key=key).first()
        if not setting:
            setting = Setting(key=key)
            db.session.add(setting)
        setting.value = val
        db.session.commit()
