"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from http import HTTPStatus
import werkzeug.exceptions as wz
import security.security as sec
from werkzeug.utils import secure_filename
import os
import data.people as ppl
import data.text as txt
import data.manuscripts.manuscript as mt
import data.manuscripts.query as qy
from data.roles import (
    get_roles,
    get_role_codes,
    get_role_descriptions,
    get_masthead_roles,
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

ENDPOINT_EP = "/endpoints"
HELLO_EP = "/hello"
TITLE_EP = "/title"
PEOPLE_EP = "/people"
TEXT_EP = "/text"
MANUSCRIPT_EP = "/manuscript"

MESSAGE = "Message"
RETURN = "return"
TITLE = "Journal About Ocean"
HELLO_RESP = "hello"
TITLE_RESP = "Title"

person_model = api.model(
    "Person",
    {
        ppl.NAME: fields.String(
            required=True, description="The person's name"
        ),
        ppl.AFFILIATION: fields.String(
            required=True, description="The person's affiliation"
        ),
        ppl.EMAIL: fields.String(
            required=True, description="The person's email"
        ),
        ppl.ROLES: fields.List(
            fields.String, required=True, description="The person's roles"
        ),
    },
)

email_model = api.model(
    "Email",
    {
        ppl.EMAIL: fields.String(
            required=True, description="The person's email"
        )
    },
)

login_model = api.model(
    "Login",
    {
        "email": fields.String(required=True, description="Your email"),
        "password": fields.String(required=True, description="Your password"),
    },
)

register_model = api.model(
    "Register",
    {
        "email": fields.String(required=True, description="Your email"),
        "password": fields.String(required=True, description="Your password"),
    },
)

# Constants for manuscript states
MANUSCRIPT_STATE_SUBMITTED = "Submitted"
MANUSCRIPT_STATE_REFEREE_REVIEW = "Referee Review"
MANUSCRIPT_STATE_AUTHOR_REVISIONS = "Author Revisions"
MANUSCRIPT_STATE_EDITOR_REVIEW = "Editor Review"
MANUSCRIPT_STATE_COPY_EDIT = "Copy Edit"
MANUSCRIPT_STATE_FORMATTING = "Formatting"
MANUSCRIPT_STATE_REJECTED = "Rejected"
MANUSCRIPT_STATE_WITHDRAWN = "Withdrawn"
MANUSCRIPT_STATE_DONE = "Done"
MANUSCRIPT_STATE_PUBLISHED = "Published"

MANUSCRIPT_STATES = [
    MANUSCRIPT_STATE_SUBMITTED,
    MANUSCRIPT_STATE_REFEREE_REVIEW,
    MANUSCRIPT_STATE_AUTHOR_REVISIONS,
    MANUSCRIPT_STATE_EDITOR_REVIEW,
    MANUSCRIPT_STATE_COPY_EDIT,
    MANUSCRIPT_STATE_FORMATTING,
    MANUSCRIPT_STATE_REJECTED,
    MANUSCRIPT_STATE_WITHDRAWN,
    MANUSCRIPT_STATE_DONE,
    MANUSCRIPT_STATE_PUBLISHED,
]

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@api.route(HELLO_EP)
class HelloWorld(Resource):
    def get(self):
        return {HELLO_RESP: "world"}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    def get(self):
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(TITLE_EP)
class JournalTitle(Resource):
    def get(self):
        return {TITLE_RESP: TITLE}


@api.route(PEOPLE_EP)
class People(Resource):
    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_FOUND, "Person not found")
    def get(self):
        try:
            people = ppl.read()
            return people, HTTPStatus.OK
        except ValueError as e:
            return {"message": str(e)}, HTTPStatus.NOT_FOUND

    @api.expect(person_model)
    @api.response(HTTPStatus.OK, "Person updated successfully")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not acceptable")
    def put(self):
        data = request.json
        name = data.get(ppl.NAME)
        affiliation = data.get(ppl.AFFILIATION)
        email = data.get(ppl.EMAIL)
        roles_input = data.get(ppl.ROLES)

        try:
            updated_person = ppl.update_person(
                name, affiliation, email, roles_input
            )
        except Exception as err:
            raise wz.NotAcceptable(f"Could not update person: {err}")

        return (
            {MESSAGE: "Person updated successfully", RETURN: updated_person},
            HTTPStatus.OK,
        )

    @api.expect(person_model)
    @api.response(HTTPStatus.CREATED, "Person added!")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not acceptable")
    def post(self):
        data = request.json
        name = data.get(ppl.NAME)
        affiliation = data.get(ppl.AFFILIATION)
        email = data.get(ppl.EMAIL)
        roles_input = data.get(ppl.ROLES)

        login_key = data.get("login_key")
        if not sec.is_permitted(
            "people", "create", email, login_key=login_key
        ):
            return {"message": "Permission denied"}, HTTPStatus.FORBIDDEN

        if isinstance(roles_input, list):
            role_kw = {"roles": roles_input}
        else:
            role_kw = {"role": roles_input}

        try:
            ret = ppl.create_person(
                name=name, affiliation=affiliation, email=email, **role_kw,
            )
        except Exception as err:
            raise wz.NotAcceptable(f"Could not add person: {err}")

        return {MESSAGE: "Person added!", RETURN: ret}, HTTPStatus.OK

    @api.expect(email_model)
    @api.response(HTTPStatus.OK, "Person deleted successfully")
    @api.response(HTTPStatus.NOT_FOUND, "Person not found")
    def delete(self):
        data = api.payload
        email = data.get(ppl.EMAIL)

        if not email:
            return {"message": "Email is required"}, HTTPStatus.BAD_REQUEST

        deleted = ppl.delete_person(email)
        if deleted:
            return {"message": "Person deleted successfully"}, HTTPStatus.OK

        return {"message": "Person not found"}, HTTPStatus.NOT_FOUND


@api.route(TEXT_EP)
class Texts(Resource):
    @api.response(HTTPStatus.OK, "Success")
    def get(self):
        try:
            texts = txt.read()
            return texts, HTTPStatus.OK
        except Exception as e:
            return {"message": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.expect(
        api.model(
            "Text",
            {
                "key": fields.String(
                    required=True, description="Unique text ID"
                ),
                "title": fields.String(
                    required=True, description="Text title"
                ),
                "text": fields.String(
                    required=True, description="Text content"
                ),
            },
        )
    )
    @api.response(HTTPStatus.CREATED, "Text created successfully")
    @api.response(HTTPStatus.BAD_REQUEST, "Text with this key already exists")
    def post(self):
        data = api.payload
        key = data.get("key")
        title = data.get("title")
        text = data.get("text")

        if not all([key, title, text]):
            return {
                "message": "Missing required fields"
            }, HTTPStatus.BAD_REQUEST

        try:
            new_text = txt.create_text(key, title, text)
            return (
                {"message": "Text created successfully", "text": new_text},
                HTTPStatus.CREATED,
            )
        except ValueError as e:
            return {"message": str(e)}, HTTPStatus.BAD_REQUEST
        except Exception:
            return (
                {"message": "Server error"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    @api.expect(
        api.model(
            "Text",
            {
                "key": fields.String(required=True),
                "title": fields.String(required=True),
                "text": fields.String(required=True),
            },
        )
    )
    @api.response(HTTPStatus.OK, "Text updated successfully")
    @api.response(HTTPStatus.NOT_FOUND, "Text not found")
    def put(self):
        data = api.payload
        key = data.get("key")
        title = data.get("title")
        text = data.get("text")

        if not all([key, title, text]):
            return {
                "message": "Missing required fields"
            }, HTTPStatus.BAD_REQUEST

        try:
            updated = txt.update_text(key, title, text)
            return (
                {"message": "Text updated successfully", "text": updated},
                HTTPStatus.OK,
            )
        except KeyError:
            return {"message": "Text not found"}, HTTPStatus.NOT_FOUND
        except Exception:
            return (
                {"message": "Server error"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )


@api.route(f"{TEXT_EP}/delete")
class TextEntry(Resource):
    @api.response(HTTPStatus.OK, "Text deleted successfully")
    @api.response(HTTPStatus.NOT_FOUND, "Text entry not found")
    def delete(self):
        data = request.get_json()
        key = data.get("key")

        try:
            txt.delete_text(key)
            return {"message": "Text deleted successfully"}, HTTPStatus.OK
        except ValueError:
            return {"message": "Text entry not found"}, HTTPStatus.NOT_FOUND


MASTHEAD = "Masthead"


@api.route(f"{PEOPLE_EP}/masthead")
class Masthead(Resource):
    def get(self):
        return {MASTHEAD: ppl.get_masthead()}


@api.route(f"{MANUSCRIPT_EP}/read")
class Manuscripts(Resource):
    def get(self):
        return mt.read()


@api.route(f"{MANUSCRIPT_EP}/states")
class ManuscriptStates(Resource):
    def get(self):
        # Get all manuscripts
        manuscripts = mt.read()

        # For each manuscript, get its current state and available actions
        state_info = {}

        for title, manuscript in manuscripts.items():
            current_state = manuscript.get(mt.STATE, "")
            available_actions = list(
                qy.get_valid_actions_by_state(current_state)
            )
            state_info[title] = {
                "current_state": current_state,
                "available_actions": available_actions,
                "_links": {
                    "update_state": {
                        "href": f"{MANUSCRIPT_EP}/update_state",
                        "method": "PUT",
                        "description": "Update manuscript state",
                    }
                },
            }

        return {
            "states": MANUSCRIPT_STATES,
            "manuscripts": state_info,
        }


manuscript_model = api.model(
    "Manuscript",
    {
        "title": fields.String(
            required=True, description="Title of the manuscript"
        ),
        "author": fields.String(required=True, description="Author name"),
        "author_email": fields.String(
            required=True, description="Author email"
        ),
        "text": fields.String(
            required=True, description="The body of the manuscript"
        ),
        "abstract": fields.String(
            required=True, description="A summary of the manuscript"
        ),
        "editor_email": fields.String(
            required=True, description="Editor email"
        ),
        "curr_state": fields.String(
            required=True, description="Current manuscript state"
        ),
        "referees": fields.Raw(
            required=False,
            description="Dictionary of referees",
            example={
                "ref@example.com": {
                    "report": "Good paper",
                    "verdict": "ACCEPT",
                }
            },
        ),
    },
)


@api.route(f"{MANUSCRIPT_EP}/create")
class ManuscriptCreate(Resource):
    @api.expect(manuscript_model)
    @api.response(HTTPStatus.OK, "Manuscript added")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not acceptable")
    def post(self):
        try:
            data = request.json
            title = data.get("title")
            author = data.get("author")
            author_email = data.get("author_email")
            text = data.get("text")
            abstract = data.get("abstract")
            editor_email = data.get("editor_email")

            ret = mt.create(
                title, author, author_email, text, abstract, editor_email,
            )
        except Exception as e:
            return (
                {
                    MESSAGE: f"Could not add manuscript: {str(e)}",
                    RETURN: None,
                },
                HTTPStatus.CONFLICT,
            )

        return {MESSAGE: "Manuscript added!", RETURN: ret}, HTTPStatus.OK


@api.route(f"{MANUSCRIPT_EP}/delete")
class ManuscriptDelete(Resource):
    @api.expect(
        api.model("DeleteRequest", {"title": fields.String(required=True)})
    )
    @api.response(HTTPStatus.OK, "Manuscript deleted successfully")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Invalid request")
    @api.response(HTTPStatus.NOT_FOUND, "Manuscript not found")
    @api.response(HTTPStatus.CONFLICT, "Conflict occurred")
    def delete(self):
        data = request.get_json(force=True)
        title = data.get("title", "").strip()

        if not title:
            return (
                {MESSAGE: "Title is required.", RETURN: None},
                HTTPStatus.NOT_ACCEPTABLE,
            )

        try:
            if not mt.exists(title):
                not_exist = f"Manuscript '{title}' does not exist."
                return {MESSAGE: not_exist, RETURN: None}, HTTPStatus.NOT_FOUND

            mt.delete(title)
        except Exception as e:
            cant_delete = f"Could not delete manuscript: {str(e)}"
            return ({MESSAGE: cant_delete, RETURN: None}, HTTPStatus.CONFLICT)

        return (
            {MESSAGE: "Manuscript deleted successfully!", RETURN: title},
            HTTPStatus.OK,
        )


@api.route(f"{MANUSCRIPT_EP}/update")
class ManuscriptUpdate(Resource):
    @api.response(HTTPStatus.OK, "Manuscript updated successfully")
    @api.response(HTTPStatus.NOT_FOUND, "Manuscript not found")
    @api.response(HTTPStatus.CONFLICT, "Error updating")
    def put(self):
        title = request.form.get("title")
        if not title:
            return (
                {"message": "Title is required", "return": None},
                HTTPStatus.BAD_REQUEST,
            )

        if not mt.exists(title):
            return (
                {
                    "message": f"Manuscript '{title}' does not exist.",
                    "return": None,
                },
                HTTPStatus.NOT_FOUND,
            )

        updates = {
            mt.AUTHOR: request.form.get("author"),
            mt.AUTHOR_EMAIL: request.form.get("author_email"),
            mt.TEXT: request.form.get("text"),
            mt.ABSTRACT: request.form.get("abstract"),
            mt.EDITOR_EMAIL: request.form.get("editor_email"),
            mt.STATE: request.form.get("state"),
        }

        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            updates[mt.FILE_PATH] = filepath

        try:
            updated = mt.update(title, updates)
            return (
                {
                    "message": "Manuscript updated successfully",
                    "return": updated.get(mt.TITLE),
                },
                HTTPStatus.OK,
            )
        except ValueError as ve:
            return {"message": str(ve), "return": None}, HTTPStatus.NOT_FOUND
        except Exception as e:
            return (
                {
                    "message":
                        f"Error updating manuscript '{title}': {str(e)}",
                    "return": None,
                },
                HTTPStatus.CONFLICT,
            )


@api.route(f"{MANUSCRIPT_EP}/receive_action")
class ReceiveAction(Resource):
    @api.response(HTTPStatus.OK, "Action processed successfully")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Invalid action or state")
    def put(self):
        try:
            title = request.json.get(mt.TITLE)
            curr_state = request.json.get(mt.STATE)
            action = request.json.get(mt.ACTION)

            if not all([title, curr_state, action]):
                return {
                    "message": "Missing required fields"
                }, HTTPStatus.BAD_REQUEST

            kwargs = {}
            manuscript = mt.read_one(title)
            if not manuscript:
                title_no_found = f'Manuscript with title "{title}" not found.'
                return ({MESSAGE: title_no_found}, HTTPStatus.NOT_FOUND)

            kwargs["manu"] = manuscript
            if mt.REFEREES in request.json:
                kwargs["ref"] = request.json.get(mt.REFEREES)

            new_state = qy.handle_action(curr_state, action, **kwargs)
            mt.update(title, {mt.STATE: new_state})
            message_to_return = "Action processed successfully"
            return (
                {"message": message_to_return, "new_state": new_state},
                HTTPStatus.OK,
            )
        except Exception as err:
            return {"message": f"Bad action: {err}"}, HTTPStatus.NOT_ACCEPTABLE


@api.route(f"{MANUSCRIPT_EP}/update_state")
class ManuscriptUpdateState(Resource):
    def put(self):
        try:
            data = request.json
            title = data.get(mt.TITLE)
            kwargs = {}
            if mt.REFEREES in data:
                kwargs["ref"] = data.get(mt.REFEREES)

            mt.update_state(title, data.get(mt.ACTION), **kwargs)
            updated = mt.read_one(title)

            return (
                {
                    "message": "Manuscript state updated successfully!",
                    "return": [title],
                    "new_state": updated[mt.STATE],
                    "history": updated[mt.HISTORY],
                },
                HTTPStatus.OK,
            )

        except Exception as err:
            return (
                {"message": f"Error updating state: {err}"},
                HTTPStatus.NOT_ACCEPTABLE,
            )


@api.route("/register")
class Register(Resource):
    @api.expect(register_model)
    @api.response(HTTPStatus.CREATED, "User registered successfully")
    @api.response(HTTPStatus.CONFLICT, "User already exists or invalid input")
    def post(self):
        data = request.json
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return {
                "message": "Email and password are required"
            }, HTTPStatus.BAD_REQUEST
        try:
            registered_email = ppl.register_user(
                email=email,
                password=password
            )
            return (
                {
                    "message": "User registered successfully",
                    "email": registered_email},
                HTTPStatus.CREATED,
            )
        except Exception as e:
            return {"message": str(e)}, HTTPStatus.CONFLICT


@api.route("/login")
class Login(Resource):
    @api.expect(login_model)
    @api.response(HTTPStatus.OK, "Login successful")
    @api.response(HTTPStatus.UNAUTHORIZED, "Invalid credentials")
    def post(self):
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {
                "message": "Email and password are required"
            }, HTTPStatus.BAD_REQUEST

        if ppl.login_user(email, password):
            return {"message": "Login successful"}, HTTPStatus.OK

        return (
            {"message": "Invalid email or password"},
            HTTPStatus.UNAUTHORIZED,
        )


@api.route("/roles")
class Roles(Resource):
    def get(self):
        role_type = request.args.get("type")

        if role_type == "codes":
            return {"data": {"role_codes": get_role_codes()}}
        if role_type == "descriptions":
            return {"data": {"role_descriptions": get_role_descriptions()}}
        if role_type == "masthead":
            return {"data": {"masthead_roles": get_masthead_roles()}}

        return {"data": {"roles": get_roles()}}


@api.route("/dev/system-info")
class SystemInfo(Resource):
    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.FORBIDDEN, "User has no access rights")
    def get(self):
        import sys
        import platform
        import flask

        info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "flask_version": flask.__version__,
            "endpoints": [rule.rule for rule in api.app.url_map.iter_rules()],
            "total_endpoints": len(list(api.app.url_map.iter_rules())),
        }
        return {"data": {"system_info": info}}


if __name__ == "__main__":
    app.run(debug=True)
    if not mt.exists("test"):
        mt.create(
            "test",
            "Author Name",
            "author@example.com",
            "Text content",
            "Abstract content",
            "editor@example.com",
        )
