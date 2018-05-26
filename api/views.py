from flask import Flask, request, jsonify, render_template
from wtforms.validators import ValidationError

from api import app, db
from api.models import entry_schema, Entry

@app.route("/set/", methods=["GET", "POST"])
def set_entry():
    if request.method == 'POST':
        json_data = request.get_json()
        if json_data and 'key' in request.json and 'value' in request.json:
            try:
                if request.is_xhr:
                    data = entry_schema.load(json_data)[0]
                else:
                    data = entry_schema.load(json_data)
            except ValidationError as err:
                return jsonify(err.messages), 422
            key, value = data['key'], data['value']
            entry = Entry.query.filter_by(key=key).first()
            if entry is None:
                entry = Entry(key=key, value=value)
                db.session.add(entry)
                db.session.commit()
                return jsonify({'value': 'The entry with key {} was succesfully created'.format(key)})
            return jsonify({'value': 'The entry {} already exist'.format(key)})
        else:
            return jsonify({'value': 'Data structure must be {"key": "your key", "value": "your value"}'}), 400
    elif request.method == 'GET':
        return render_template('set.html')

@app.route("/get/", methods=["GET"])
@app.route("/get/<key>", methods=["GET"])
def get_entry(key=None):
    if key is None and not request.is_xhr:
        return render_template('get.html')

    entry = Entry.query.filter_by(key=key).first()
    if entry:
        return entry_schema.jsonify(entry)
    else:
        return jsonify({'value': 'No value with this key in db'})