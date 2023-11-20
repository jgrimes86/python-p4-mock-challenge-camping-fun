#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):

    def get(self):
        campers = [camper.to_dict(rules=('-signups',)) for camper in Camper.query.all()]
        return make_response(campers, 200)

    def post(self):
        params = request.json
        try:
            new_camper = Camper(name=params['name'], age=params['age'])
        except ValueError as v_error:
            return make_response({"errors": [str(v_error)]}, 400)

        db.session.add(new_camper)
        db.session.commit()
        response = make_response(
            new_camper.to_dict(rules=('-signups',)),
            200
        )
        return response

api.add_resource(Campers, '/campers')

class CampersById(Resource):
    
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(camper.to_dict(), 200)

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        
        params = request.json
        try:
            for attr in params:
                setattr(camper, attr, params[attr])
        except ValueError as v_error:
            return make_response({"errors": [str(v_error)]}, 400)

        db.session.commit()
        response = make_response(
            camper.to_dict(rules=('-signups',)),
            200
        )
        return response

api.add_resource(CampersById, '/campers/<int:id>')


@app.route('/activities')
def get_activities():
    activities = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]
    return make_response(activities, 200)

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    if request.method == 'DELETE':
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return make_response({"error": "Activity not found"}, 404)
        db.session.delete(activity)
        db.session.commit()
        return make_response({}, 204)

@app.route('/signups', methods=['POST'])
def post_signup():
    params = request.json
    try:
        new_signup = Signup(time=params['time'], camper_id=params['camper_id'], activity_id=params['activity_id'])
    except ValueError as v_error:
        return make_response({"errors": [str(v_error)]}, 400)

    db.session.add(new_signup)
    db.session.commit()
    response = make_response(
        new_signup.to_dict(),
        200
    )
    return response



if __name__ == '__main__':
    app.run(port=5555, debug=True)
