from api import db, ma

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80))
    value = db.Column(db.String(80))

    def __init__(self, key, value):
        self.key = key
        self.value = value

class EntrySchema(ma.Schema):
    class Meta:
        fields = ('key', 'value')

entry_schema = EntrySchema()