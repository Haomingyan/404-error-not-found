"""
This module interfaces to our user data.
"""

import re

import data.roles as rls

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

CHAR_OR_DIGIT = '[A-Za-z0-9]'


def is_valid_email(email: str) -> bool:
    return re.match(f"{CHAR_OR_DIGIT}.*@{CHAR_OR_DIGIT}.*", email)


def is_valid_person(name: str, affiliation: str, email: str,
                    role: str) -> bool:
    if email in people_dict:
        raise ValueError(f'Adding duplicate {email=}')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
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


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    people = people_dict
    return people


# def delete_person(_id):
#     people = read()
#     if _id in people:
#         del people[_id]
#         return _id
#     else:
#         return None
def delete_person(email):
    if email in people_dict:
        del people_dict[email]
        return email
    else:
        return None


def create_person(name: str, affiliation: str, email: str):
    print("Current people_dict:", people_dict)
    if email in people_dict:
        raise ValueError(f'Adding duplicate {email=}')
    people_dict[email] = {NAME: name, AFFILIATION: affiliation,
                          EMAIL: email}
    return email


def has_arole(person: dict, role: str):
    if role in person[ROLES]:
        return True
    else:
        return False


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


def update_person(name: str, affiliation: str,
                  email: str):
    """
    Update the details of an existing person.
    If the person with the given email exists,
    update their name and affiliation.
    """
    print("Current people_dict:", people_dict)
    if email in people_dict:
        # Update the existing person's details
        people_dict[email][NAME] = name
        people_dict[email][AFFILIATION] = affiliation
        return people_dict[email]
    else:
        # If the person does not exist, raise an error
        raise ValueError(f'Person with email {email} does not exist')
