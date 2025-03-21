"""
This module interfaces to our user data.
"""

import re

import data.db_connect as dbc

import data.roles as rls

from werkzeug.security import generate_password_hash, check_password_hash

PEOPLE_COLLECT = 'people'
USER_COLLECT = 'users'

MIN_USER_NAME_LEN = 2

# fields
NAME = 'name'
ROLES = 'roles'
AFFILIATION = 'affiliation'
EMAIL = 'email'

TEST_EMAIL = 'ejc369@nyu.edu'
DEL_EMAIL = 'delete@nyu.edu'

people_dict = {
    TEST_EMAIL: {
        NAME: 'Eugene Callahan',
        ROLES: [],
        AFFILIATION: 'NYU',
        EMAIL: TEST_EMAIL,
    },
    DEL_EMAIL: {
        NAME: 'Another Person',
        ROLES: [],
        AFFILIATION: 'NYU',
        EMAIL: DEL_EMAIL,
    },
}

client = dbc.connect_db()
print(f'{client=}')

first_part = (
    r"[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9!#$%&'*+/=?^_{|}~.-]*[a-zA-Z0-9])"
)
second_part = r"[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*"
third_part = r"[a-zA-Z]{2,6}"

EMAIL_REGEX = rf"^{first_part}@{second_part}\.{third_part}$"


def is_valid_email(email: str) -> bool:
    return bool(re.match(EMAIL_REGEX, email))


def is_valid_person(name: str, affiliation: str, email: str,
                    role: str = None, roles: list = None) -> bool:
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if role:
        if not rls.is_valid(role):
            raise ValueError(f'Invalid role: {role}')
    elif roles:
        for role in roles:
            if not rls.is_valid(role):
                raise ValueError(f'Invalid role: {role}')
    return True


def get_person(email):
    """
    Retrieve the details of a person by their email
    Returns the person's data if found, else None
    """
    if email in people_dict:
        return people_dict[email]
    else:
        return None


def read() -> dict:
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    people = dbc.read_dict(PEOPLE_COLLECT, EMAIL)
    if not people:
        print("There is no people in the mongodb")
    print(f'{people=}')
    return people


def read_one(email: str) -> dict:
    """
    Return a person record if email present in DB,
    else None.
    """
    return dbc.read_one(PEOPLE_COLLECT, {EMAIL: email})


def exists(email: str) -> bool:
    return read_one(email) is not None


def delete_person(email: str):
    """
    Delete a person from MongoDB by email.
    If the person does not exist, print a message and return None.
    """
    person = dbc.fetch_one(PEOPLE_COLLECT, {"email": email})
    if person is None:
        print(f'No person found with {email=}')
        return None
    result = dbc.delete(PEOPLE_COLLECT, {"email": email})
    print(result)
    print(f"Deleted {email=}")
    return email


def create_person(name: str, affiliation: str, email: str, role: str):
    if exists(email):
        raise ValueError(f'Adding duplicate {email=}')
    if is_valid_person(name, affiliation, email, role=role):
        roles = []
        if role:
            roles.append(role)
        person = {NAME: name, AFFILIATION: affiliation,
                  EMAIL: email, ROLES: roles}
        print(person)
        dbc.create(PEOPLE_COLLECT, person)
        return email


def has_arole(person: dict, role: str):
    if role in person[ROLES]:
        return True
    else:
        return False


MH_FIELDS = [NAME, AFFILIATION]


def get_mh_fields(journal_code=None) -> list:
    return MH_FIELDS


def create_mh_rec(person: dict) -> dict:
    mh_rec = {}
    for field in get_mh_fields():
        mh_rec[field] = person.get(field, '')
    return mh_rec


def get_masthead():
    masthead = {}
    mh_roles = rls.get_masthead_roles()
    for mh_role, text in mh_roles.items():
        people_w_role = {}
        for person_email, person_data in read().items():
            if has_arole(person_data, mh_role):
                people_w_role[person_email] = person_data
        masthead[text] = people_w_role
    return masthead


def update_person(name: str, affiliation: str, email: str, roles: list):
    """
    Update the details of an existing person in MongoDB.
    If the person with the given email exists,
    update their name, affiliation, and roles (overwriting existing roles).
    """
    # Fetch the person from MongoDB
    person = dbc.fetch_one(PEOPLE_COLLECT, {"email": email})

    if person:
        # Prepare the fields to update
        update_fields = {
            NAME: name,
            AFFILIATION: affiliation,
            ROLES: roles
        }

        # Use update_doc to apply the updates
        dbc.update_doc(PEOPLE_COLLECT, {"email": email}, update_fields)

        # Return the updated document for confirmation
        return dbc.fetch_one(PEOPLE_COLLECT, {"email": email})
    else:
        # Raise an error if the person does not exist in MongoDB
        raise ValueError(f'Person with email {email} does not exist')


PASSWORD = 'password'


def register_user(email: str, password: str):
    existing_user = dbc.read_one(USER_COLLECT, {EMAIL: email})
    if existing_user:
        raise ValueError(f'User already exists: {email}')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if not password:
        raise ValueError('Password is required.')

    hashed_pw = generate_password_hash(password)

    user = {
        EMAIL: email,
        PASSWORD: hashed_pw,
    }

    dbc.create(USER_COLLECT, user)
    print(f'User registered: {email}')
    return email


def login_user(email: str, password: str) -> bool:
    person = dbc.fetch_one(USER_COLLECT, {EMAIL: email})
    if person is None:
        return False
    stored_pw = person.get(PASSWORD)
    if not stored_pw:
        return False
    return check_password_hash(stored_pw, password)
