import pytest
import data.people as ppl
from data.roles import TEST_CODE as TEST_ROLE_CODE
from data.people import get_person, TEST_EMAIL, NAME, ROLES, AFFILIATION, EMAIL
from data.people import get_masthead, create_person, delete_person, NAME, ROLES, EMAIL
from data.roles import TEST_CODE
from unittest.mock import patch
import data.db_connect as dbc

TEMP_EMAIL = 'temp_person@temp.org'

START_WITH_SYMBOL = '.kajshd@nyu.edu'
NO_NAME = "@nyu.edu"
NO_AT = "tempdadada"
PEOPLE_COLLECT = 'people'

def test_is_valid_email_start_with_symbol():
    assert not ppl.is_valid_email(START_WITH_SYMBOL)

def test_is_valid_no_name():
    assert not ppl.is_valid_email(NO_NAME)


@pytest.fixture(scope='function')
def temp_person():
    _id = ppl.create_person('Joe Smith', 'NYU', TEMP_EMAIL, TEST_ROLE_CODE)
    yield _id
    ppl.delete_person(_id)


@pytest.fixture
def valid_person_data():
    return {
        "name": "Test User",
        "affiliation": "NYU",
        "email": TEMP_EMAIL,
        "role": TEST_ROLE_CODE
    }

def test_has_role(temp_person):
    person_rec = ppl.read_one(temp_person)
    assert ppl.has_arole(person_rec, TEST_ROLE_CODE)

def test_has_no_role(temp_person):
    person_rec = ppl.read_one(temp_person)
    assert not ppl.has_arole(person_rec, 'Does not have a role')


def test_get_mh_fields():
    flds = ppl.get_mh_fields()
    assert isinstance(flds, list)
    assert len(flds) > 0


def test_create_mh_rec(temp_person):
    person_rec = ppl.read_one(temp_person)
    mh_rec = ppl.create_mh_rec(person_rec)
    assert isinstance(mh_rec, dict)
    for field in ppl.MH_FIELDS:
        assert field in mh_rec


def test_read():
    people = ppl.read()
    assert isinstance(people, dict)
    assert len(people) > 0
    # check for string IDs:
    for _id, person in people.items():
        assert isinstance(_id, str)
        assert ppl.NAME in person

def test_read_one(temp_person):
    assert ppl.read_one(temp_person) is not None

def test_read_one_nonexistent():
    assert ppl.read_one('nonexistent@nyu.edu') is None

def test_is_valid_email_no_at():
    assert not ppl.is_valid_email(NO_AT)

def test_delete_person():
    # Define test data
    DEL_EMAIL = 'delete_me@nyu.edu'
    NAME = 'Delete Me'
    AFFILIATION = 'NYU'

    # First, create the person to be deleted
    ppl.create_person(NAME, AFFILIATION, DEL_EMAIL, TEST_CODE)

    # Verify that the person was created in the database
    person = dbc.fetch_one(PEOPLE_COLLECT, {EMAIL: DEL_EMAIL})
    assert person is not None, "Person to be deleted was not created."

    # Test deleting the existing person
    deleted_email = ppl.delete_person(DEL_EMAIL)
    assert deleted_email == DEL_EMAIL, "Deleted email does not match."

    # Verify that the person was deleted from the database
    person = dbc.fetch_one(PEOPLE_COLLECT, {EMAIL: DEL_EMAIL})
    assert person is None, "Person was not deleted from the database."

    # Test deleting a non-existing person
    non_existing_email = 'nonexistent@nyu.edu'
    deleted_email = ppl.delete_person(non_existing_email)
    assert deleted_email is None, "Deleting a non-existing person should return None."


def test_get_person():
    # Test with an existing email
    existing_email = TEST_EMAIL
    expected_person = {
        NAME: 'Eugene Callahan',
        ROLES: [],
        AFFILIATION: 'NYU',
        EMAIL: TEST_EMAIL,
    }
    result = get_person(existing_email)
    if result == expected_person:
        print("Test passed: Existing email returns correct data.")
    else:
        print("Test failed: Existing email does not return correct data.")

    # Test with a non-existing email
    non_existing_email = 'nonexistent@example.com'
    result = get_person(non_existing_email)
    if result is None:
        print("Test passed: Non-existing email returns None.")
    else:
        print("Test failed: Non-existing email does not return None.")

ADD_EMAIL = 'joe@nyu.edu'


def test_create_person():
    # Attempt to create the person
    ppl.create_person('Joe Smith', 'NYU', ADD_EMAIL, TEST_CODE)

    # Verify that the person was created in the database
    created_person = dbc.fetch_one(PEOPLE_COLLECT, {EMAIL: ADD_EMAIL})
    assert created_person is not None, "Person was not created in the database."
    assert created_person[EMAIL] == ADD_EMAIL, "Email does not match."
    assert created_person[NAME] == 'Joe Smith', "Name does not match."
    assert created_person[AFFILIATION] == 'NYU', "Affiliation does not match."
    assert TEST_CODE in created_person[ROLES], "Role does not match."

    # Clean up by removing the test document from the collection
    dbc.delete(PEOPLE_COLLECT, {EMAIL: ADD_EMAIL})


# Second time creating temp_person (duplicate)

def test_create_duplicate_person():
    with pytest.raises(ValueError, match="Adding duplicate email"):
        ppl.create_person('Joe Smith', 'NYU', TEMP_EMAIL, 'AU')


UPDATE_EMAIL = TEST_EMAIL
NEW_NAME = 'Eugene Callahan Jr.'
NEW_AFFILIATION = 'Columbia University'
NEW_ROLES = ['Professor']

def test_is_valid_person():
    # Test with valid inputs
    with patch('data.roles.is_valid', return_value=True):
        try:
            assert ppl.is_valid_person(name='John Doe', affiliation='NYU', email='johndoe@nyu.edu', role='editor')
            print("Test passed: Valid person with role.")
        except ValueError as e:
            assert False, f"Test failed: {str(e)}"

    # Test with valid inputs and multiple roles
    with patch('data.roles.is_valid', return_value=True):
        try:
            assert ppl.is_valid_person(name='Jane Smith', affiliation='NYU', email='janesmith@nyu.edu', roles=['editor', 'reviewer'])
            print("Test passed: Valid person with multiple roles.")
        except ValueError as e:
            assert False, f"Test failed: {str(e)}"

    # Test with invalid email
    try:
        ppl.is_valid_person(name='Invalid Email', affiliation='NYU', email='invalid-email')
    except ValueError as e:
        assert str(e) == 'Invalid email: invalid-email', "Test failed: Incorrect error message for invalid email."
    else:
        assert False, "Test failed: Expected ValueError for invalid email."
    print("Test passed: Invalid email raises ValueError.")

    # Test with invalid role
    with patch('data.roles.is_valid', return_value=False):
        try:
            ppl.is_valid_person(name='Invalid Role', affiliation='NYU', email='invalidrole@nyu.edu', role='invalid_role')
        except ValueError as e:
            assert str(e) == 'Invalid role: invalid_role', "Test failed: Incorrect error message for invalid role."
        else:
            assert False, "Test failed: Expected ValueError for invalid role."
    print("Test passed: Invalid role raises ValueError.")

def test_get_masthead():
    # Emails for test people
    masthead_email = 'editor@nyu.edu'
    non_masthead_email = 'author@nyu.edu'

    # Ensure no previous data remains
    delete_person(masthead_email)
    delete_person(non_masthead_email)

    # Create a person (assumed to be part of the masthead)
    masthead_person = {
        NAME: 'Editor Person',
        AFFILIATION: 'NYU',
        EMAIL: masthead_email,
        ROLES: ['editor']
    }
    ppl.people_dict[masthead_email] = masthead_person

    # Create another person (assumed to not be part of the masthead)
    non_masthead_person = {
        NAME: 'Author Person',
        AFFILIATION: 'NYU',
        EMAIL: non_masthead_email,
        ROLES: []
    }
    ppl.people_dict[non_masthead_email] = non_masthead_person

    # Mock the roles used in get_masthead
    with patch('data.roles.get_masthead_roles') as mock_get_masthead_roles:
        mock_get_masthead_roles.return_value = {
            'editor': 'Editor'
        }

        # Call get_masthead to retrieve the masthead people
        masthead = get_masthead()

        # Verify that the masthead person is included
        assert masthead_email in masthead['Editor']
        assert masthead['Editor'][masthead_email][NAME] == 'Editor Person'

        # Verify that the non-masthead person is not included
        assert non_masthead_email not in masthead['Editor']

    # Clean up test data
    delete_person(masthead_email)
    delete_person(non_masthead_email)

    print("Test passed: get_masthead returns correct masthead people and excludes non-masthead people.")

def test_update_person():
    UPDATE_EMAIL = 'joe.smith@nyu.edu'
    INITIAL_NAME = 'Joe Smith'
    INITIAL_AFFILIATION = 'NYU'
    NEW_NAME = 'Joseph Smith'
    NEW_AFFILIATION = 'New York University'
    NEW_ROLE = 'editor'

    ppl.create_person(INITIAL_NAME, INITIAL_AFFILIATION, UPDATE_EMAIL, TEST_CODE)

    created_person = dbc.fetch_one(PEOPLE_COLLECT, {EMAIL: UPDATE_EMAIL})
    assert created_person is not None, "Person was not created in the database."
    assert created_person[EMAIL] == UPDATE_EMAIL, "Email does not match."
    assert created_person[NAME] == INITIAL_NAME, "Name does not match."
    assert created_person[AFFILIATION] == INITIAL_AFFILIATION, "Affiliation does not match."
    assert TEST_CODE in created_person.get(ROLES, []), "Role does not match."

    try:
        updated_person = ppl.update_person(
            name=NEW_NAME,
            affiliation=NEW_AFFILIATION,
            email=UPDATE_EMAIL,
            role=NEW_ROLE
        )
    except ValueError as e:
        assert False, f"Test failed: {str(e)}"

    assert updated_person[NAME] == NEW_NAME, "Name was not updated correctly."
    assert updated_person[AFFILIATION] == NEW_AFFILIATION, "Affiliation was not updated correctly."
    assert NEW_ROLE in updated_person.get(ROLES, []), "Role was not updated correctly."

    updated_person_from_db = dbc.fetch_one(PEOPLE_COLLECT, {EMAIL: UPDATE_EMAIL})
    assert updated_person_from_db[NAME] == NEW_NAME, "Name in DB was not updated correctly."
    assert updated_person_from_db[AFFILIATION] == NEW_AFFILIATION, "Affiliation in DB was not updated correctly."
    assert NEW_ROLE in updated_person_from_db.get(ROLES, []), "Role in DB was not updated correctly."

    dbc.delete(PEOPLE_COLLECT, {EMAIL: UPDATE_EMAIL})

    print("Test passed: Person updated successfully.")

    NON_EXISTING_EMAIL = 'nonexistent@example.com'
    try:
        ppl.update_person(
            name='Non Existent',
            affiliation='None',
            email=NON_EXISTING_EMAIL,
            role='some_role'
        )
    except ValueError as e:
        assert str(e) == f'Person with email {NON_EXISTING_EMAIL} does not exist', "Test failed: Incorrect error message."
        print("Test passed: Updating non-existing person returns ValueError.")
    else:
        assert False, "Test failed: Expected ValueError for non-existing person."

def test_update_nonexistent_person_exception():
    with pytest.raises(ValueError, match=r"Person with email .* does not exist"):
        ppl.update_person(
            name="Nonexistent Person",
            affiliation="Unknown",
            email="nonexistent@example.com",
            role="author"
        )

