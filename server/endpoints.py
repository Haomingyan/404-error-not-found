"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask, request  # , request
from flask_restx import Resource, Api, fields  # Namespace , fields
from flask_cors import CORS
from http import HTTPStatus

import data.people as ppl
import data.text as txt
# from data.people import people_dict

# import werkzeug.exceptions as wz

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
TITLE_EP = '/title'
TITLE_RESP = 'Title'
TITLE = 'Journal About Ocean'
PEOPLE_EP = '/people'
TEXT_EP = '/texts'

person_model = api.model('Person', {
    'name': fields.String(required=True, description='The person\'s name'),
    'affiliation': fields.String(required=True,
                                 description='The person\'s affiliation'),
    'email': fields.String(required=True, description='The person\'s email')
})

email_model = api.model('Email', {
    'email': fields.String(required=True, description="The person's email")
})


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {HELLO_RESP: 'world'}


@api.route('/endpoints')
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(TITLE_EP)
class JournalTitle(Resource):
    """
    This class handles creating, reading,
     updating, and deleting the journal title.
    """
    def get(self):
        """
        Retrieve the journal title
        """
        return {TITLE_RESP: TITLE}


@api.route(PEOPLE_EP)
class People(Resource):
    """
    This class handles creating, reading, updating
    and deleting journal people.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Person not found')
    def get(self):
        """
        read the journal people.
        """
        try:
            people = ppl.read()
            return people, HTTPStatus.OK
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.NOT_FOUND

    @api.expect(person_model)
    def put(self):
        """
        Update an existing person.
        """
        data = api.payload
        try:
            updated_person = ppl.update_person(
                data['name'],
                data['affiliation'],
                data['email'])
            return {'message': 'Person updated successfully',
                    'person': updated_person}, 200
        except ValueError as e:
            return {'message': str(e)}, 400

    @api.expect(person_model)
    def post(self):
        """
        Create a new person.
        """
        data = request.json
        try:
            new_person = ppl.create_person(
                data['name'],
                data['affiliation'],
                data['email'])  #
            return {'message': 'Person created successfully',
                    'person': new_person,
                    }, 201
        except ValueError as e:
            return {'message': str(e)}, 400

    @api.expect(email_model)
    @api.response(HTTPStatus.OK, 'Person deleted successfully')
    @api.response(HTTPStatus.NOT_FOUND, 'Person not found')
    def delete(self):
        """
        Delete a person.
        """
        data = api.payload
        email = data.get('email')
        if not email:
            return {'message': 'Email is required'}, 400

        deleted_person = ppl.delete_person(email)
        if deleted_person:
            return {'message': 'Person deleted successfully'}, HTTPStatus.OK
        else:
            return {'message': 'Person not found'}, HTTPStatus.NOT_FOUND


@api.route(TEXT_EP)
class Texts(Resource):
    """
    This class handles reading all the text entries.
    """
    @api.response(HTTPStatus.OK, 'Success')
    def get(self):
        """
        Retrieve all text entries.
        """
        try:
            texts = txt.read()
            return texts, HTTPStatus.OK
        except Exception as e:
            return {'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == '__main__':
    app.run(debug=True)
