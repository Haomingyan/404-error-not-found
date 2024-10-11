"""
This module interfaces to our user data.
"""


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

def get_person(email):
    """
    Retrieve the details of a person by their email.
    Returns the person's data if found, else None.
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

def update_person(name: str, affiliation: str, email: str):
    """
    Update the details of an existing person.
    If the person with the given email exists, update their name and affiliation.
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

