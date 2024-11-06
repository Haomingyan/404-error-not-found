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


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    people = people_dict
    return people


def read_one(email: str) -> dict:
    """
    Return a person record if email present in DB,
    else None.
    """
    return people_dict.get(email)


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


def create_person(name: str, affiliation: str, email: str, role: str):
    if email in people_dict:
        raise ValueError(f'Adding duplicate {email=}')
    if is_valid_person(name, affiliation, email, role=role):
        roles = []
        if role:
            roles.append(role)
        people_dict[email] = {NAME: name, AFFILIATION: affiliation,
                              EMAIL: email, ROLES: roles}
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


def update_person(name: str, affiliation: str, email: str, role: str):
    """
    Update the details of an existing person.
    If the person with the given email exists,
    update their name, affiliation, and role.
    """
    print("Current people_dict:", people_dict)
    if email in people_dict:
        # Update the existing person's details
        people_dict[email][NAME] = name
        people_dict[email][AFFILIATION] = affiliation
        if role and role not in people_dict[email][ROLES]:
            people_dict[email][ROLES].append(role)  # 添加新角色，避免重复
        return people_dict[email]
    else:
        # If the person does not exist, raise an error
        raise ValueError(f'Person with email {email} does not exist')
