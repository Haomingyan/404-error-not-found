"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask, request  # , request
from flask_restx import Resource, Api, fields  # Namespace , fields
from flask_cors import CORS
from http import HTTPStatus

import werkzeug.exceptions as wz
import data.people as ppl
import data.text as txt
import data.manuscripts.manuscript as mt
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
TEXT_EP = '/text'
MESSAGE = 'Message'
RETURN = 'return'
MANUSCRIPT_EP = '/manuscript'

person_model = api.model('Person', {
    'name': fields.String(required=True, description='The person\'s name'),
    'affiliation': fields.String(required=True,
                                 description='The person\'s affiliation'),
    'email': fields.String(required=True, description='The person\'s email'),
    'role': fields.String(required=True, description='The person\'s role')
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
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    def put(self):
        """
        Update an existing person.
        """
        data = request.json
        name = data.get('name')
        affiliation = data.get('affiliation')
        email = data.get('email')
        role = data.get('role')
        try:
            updated_person = ppl.update_person(name, affiliation, email, role)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update person: {err}')
        return {
            MESSAGE: 'Person updated successfully',
            RETURN: updated_person,
        }, HTTPStatus.OK

    @api.expect(person_model)
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    def post(self):
        """
        Create a new person.
        """
        try:
            name = request.json.get(ppl.NAME)
            affiliation = request.json.get(ppl.AFFILIATION)
            email = request.json.get(ppl.EMAIL)
            role = request.json.get(ppl.ROLES)
            ret = ppl.create_person(name, affiliation, email, role)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add person: '
                                   f'{err=}')
        return {
            MESSAGE: 'Person added!',
            RETURN: ret,
        }

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

    @api.expect(api.model('Text', {
        'key': fields.String(required=True,
                             description='A unique identifier '
                                         'for the text entry'),
        'title': fields.String(required=True,
                               description='The title of the text entry'),
        'text': fields.String(required=True,
                              description='The content of the text entry')
    }))
    @api.response(HTTPStatus.CREATED, 'Text created successfully')
    @api.response(HTTPStatus.BAD_REQUEST, 'Text with this key already exists')
    def post(self):
        """
        Create a new text entry.
        """
        data = api.payload
        try:
            new_text = txt.create_text(data['key'],
                                       data['title'],
                                       data['text'])
            return {'message': 'Text created successfully',
                    'text': new_text}, HTTPStatus.CREATED
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            return {'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.expect(api.model('Text', {
        'key': fields.String(required=True,
                             description='A unique identifier '
                                         'for the text entry'),
        'title': fields.String(required=True,
                               description='The title of the text entry'),
        'text': fields.String(required=True,
                              description='The content of the text entry')
    }))
    @api.response(HTTPStatus.OK, 'Text updated successfully')
    @api.response(HTTPStatus.NOT_FOUND, 'Text with this key does not exist')
    def put(self):
        """
        Update an existing text entry.
        """
        data = api.payload
        try:
            updated_text = txt.update_text(data['key'],
                                           data['title'],
                                           data['text'])
            return {'message': 'Text updated successfully',
                    'text': updated_text}, HTTPStatus.OK
        except KeyError:
            return ({'message': 'Text with this key does not exist'},
                    HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({'message': str(e)},
                    HTTPStatus.INTERNAL_SERVER_ERROR)


@api.route(f'{TEXT_EP}/<string:key>')
class TextEntry(Resource):
    @api.response(HTTPStatus.OK, 'Text deleted successfully')
    @api.response(HTTPStatus.NOT_FOUND, 'Text entry not found')
    def delete(self, key):
        """
        Delete a text entry by key from the URL path parameter.
        """
        try:
            txt.delete_text(key)
            return {'message': 'Text deleted successfully'}, HTTPStatus.OK
        except ValueError:
            return {'message': 'Text entry not found'}, HTTPStatus.NOT_FOUND


@api.route(f'{MANUSCRIPT_EP}/read')
class Manuscripts(Resource):
    """
    This class handles reading manuscripts.
    """
    def get(self):
        """
        Retrieve all manuscripts.
        """
        return mt.read()


manuscript_model = api.model('Manuscript', {
    'title': fields.String(required=True,
                           description='Title of the manuscript'),
    'author': fields.String(required=True,
                            description='Author name'),
    'author_email': fields.String(required=True,
                                  description='Author email'),
    'text': fields.String(required=True,
                          description='The body of the manuscript'),
    'abstract': fields.String(required=True,
                              description='A summary of the manuscript'),
    'editor_email': fields.String(required=True,
                                  description='Editor email'),
    'referees': fields.Raw(required=False,
                           description='Dictionary of referees',
                           example={
                               "referee_email@example.com": {
                                   "report": "Good paper",
                                   "verdict": "ACCEPT"
                               }
                           }),
})


@api.route(f'{MANUSCRIPT_EP}/create')
class ManuscriptCreate(Resource):
    """
    This class handles creating a new manuscript.
    """
    @api.expect(manuscript_model)
    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable.')
    def post(self):
        """
        Create a new manuscript.
        """
        try:
            data = request.json

            title = data.get('title')
            author = data.get('author')
            author_email = data.get('author_email')
            text = data.get('text')
            abstract = data.get('abstract')
            editor_email = data.get('editor_email')

            ret = mt.create(title, author,
                            author_email, text,
                            abstract, editor_email)
        except Exception as e:
            return {
                MESSAGE: f'Could not add manuscript: {str(e)}',
                RETURN: None,
            }, HTTPStatus.CONFLICT

        return {
            MESSAGE: 'Manuscript added!',
            RETURN: ret,
        }, HTTPStatus.OK


@api.route(f'{MANUSCRIPT_EP}/delete')
class ManuscriptDelete(Resource):
    """
    This class handles deleting a manuscript by title.
    """
    @api.expect(api.model('DeleteRequest', {
        'title': fields.String(required=True,
                               description='Title of the manuscript to delete')
    }))
    @api.response(HTTPStatus.OK,
                  'Manuscript deleted successfully.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE,
                  'Invalid request (e.g., missing title).')
    @api.response(HTTPStatus.NOT_FOUND, 'Manuscript not found.')
    @api.response(HTTPStatus.CONFLICT, 'Conflict occurred while deleting.')
    def delete(self):
        """
        Delete a manuscript.
        """
        data = request.get_json(force=True)
        title = data.get('title', '').strip()

        if not title:
            return {
                MESSAGE: "Title is required.",
                RETURN: None,
            }, HTTPStatus.NOT_ACCEPTABLE

        try:
            if not mt.exists(title):
                return {
                    MESSAGE: f"Manuscript '{title}' does not exist.",
                    RETURN: None,
                }, HTTPStatus.NOT_FOUND

            mt.delete(title)

        except Exception as e:
            return {
                MESSAGE: f"Could not delete manuscript: {str(e)}",
                RETURN: None,
            }, HTTPStatus.CONFLICT

        return {
            MESSAGE: "Manuscript deleted successfully!",
            RETURN: title,
        }, HTTPStatus.OK


@api.route(f'/{MANUSCRIPT_EP}/update')
class ManuscriptUpdate(Resource):
    @api.expect(manuscript_model)
    @api.response(HTTPStatus.OK, 'Manuscript updated successfully.')
    @api.response(HTTPStatus.NOT_FOUND, 'Manuscript not found.')
    @api.response(HTTPStatus.CONFLICT, 'Error updating the manuscript.')
    def put(self):
        """
        Update an existing manuscript.
        """
        data = request.json
        title = data.get('title')
        author = data.get('author')
        author_email = data.get('author_email')
        text = data.get('text')
        abstract = data.get('abstract')
        editor_email = data.get('editor_email')

        # Check if the manuscript exists before attempting update
        if not mt.exists(title):
            return {
                MESSAGE: f"Manuscript '{title}' does not exist.",
                RETURN: None,
            }, HTTPStatus.NOT_FOUND

        updates = {
            mt.AUTHOR: author,
            mt.AUTHOR_EMAIL: author_email,
            mt.TEXT: text,
            mt.ABSTRACT: abstract,
            mt.EDITOR_EMAIL: editor_email,
        }

        try:
            updated_manuscript = mt.update(title, updates)
            return {
                MESSAGE: "Manuscript updated successfully.",
                RETURN: updated_manuscript[mt.TITLE],
            }, HTTPStatus.OK
        except ValueError as ve:
            return {
                MESSAGE: str(ve),
                RETURN: None,
            }, HTTPStatus.NOT_FOUND
        except Exception as e:
            return {
                MESSAGE: f"Error updating manuscript '{title}': {str(e)}",
                RETURN: None,
            }, HTTPStatus.CONFLICT


if __name__ == '__main__':
    app.run(debug=True)
