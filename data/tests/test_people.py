# import data.users as usrs
import data.people as ppl
from data.people import get_person, TEST_EMAIL, NAME, ROLES, AFFILIATION, EMAIL
from data.people import get_masthead, create_person, delete_person, NAME, ROLES, EMAIL
from data.roles import TEST_CODE
import unittest
from unittest.mock import patch

def test_read():
    people = ppl.read()
    assert isinstance(people, dict)
    assert len(people) > 0
    # check for string IDs:
    for _id, person in people.items():
        assert isinstance(_id, str)
        assert ppl.NAME in person

def test_delete_person():
    # Test deleting an existing person
    people = ppl.read()
    assert ppl.DEL_EMAIL in people
    deleted_person = ppl.delete_person(ppl.DEL_EMAIL)
    assert deleted_person == ppl.DEL_EMAIL
    updated_people = ppl.read()
    assert ppl.DEL_EMAIL not in updated_people

    # Test deleting a non-existing person
    non_existing_email = 'nonexistent@nyu.edu'
    deleted_person = ppl.delete_person(non_existing_email)
    assert deleted_person is None

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
    people = ppl.read()
    assert ADD_EMAIL not in people
    ppl.create_person('Joe Smith', 'NYU', ADD_EMAIL, TEST_CODE)
    people = ppl.read()
    assert ADD_EMAIL in people

UPDATE_EMAIL = TEST_EMAIL
NEW_NAME = 'Eugene Callahan Jr.'
NEW_AFFILIATION = 'Columbia University'
NEW_ROLES = ['Professor']

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
    # Test updating an existing person
    person = get_person(UPDATE_EMAIL)
    assert person is not None, "Test failed: Person does not exist."

    # Update the person's information
    try:
        updated_person = ppl.update_person(name=NEW_NAME, affiliation=NEW_AFFILIATION, email=UPDATE_EMAIL)
    except ValueError as e:
        assert False, f"Test failed: {str(e)}"

    # Verify that the person's information has been updated
    assert updated_person[NAME] == NEW_NAME
    assert updated_person[AFFILIATION] == NEW_AFFILIATION

    # Fetch the updated person and check
    updated_person_from_db = get_person(UPDATE_EMAIL)
    assert updated_person_from_db[NAME] == NEW_NAME
    assert updated_person_from_db[AFFILIATION] == NEW_AFFILIATION
    print("Test passed: Existing person updated successfully.")

    # Test updating a non-existing person
    non_existing_email = 'nonexistent@example.com'
    try:
        ppl.update_person(name='Non Existent', affiliation='None', email=non_existing_email)
    except ValueError as e:
        assert str(e) == f'Person with email {non_existing_email} does not exist', "Test failed: Incorrect error message."
    else:
        assert False, "Test failed: Expected ValueError for non-existing person."
    print("Test passed: Updating non-existing person returns ValueError.")



# def test_get_masthead():
#     # Emails for test people
#     masthead_email = 'editor@nyu.edu'
#     non_masthead_email = 'author@nyu.edu'
#
#     # Ensure no previous data remains
#     delete_person(masthead_email)
#     delete_person(non_masthead_email)
#
#     # Create a person (assumed to be part of the masthead)
#     masthead_person = {
#         NAME: 'Editor Person',
#         ppl.AFFILIATION: 'NYU',
#         EMAIL: masthead_email
#     }
#     ppl.people_dict[masthead_email] = masthead_person
#
#     # Create another person (assumed to not be part of the masthead)
#     non_masthead_person = {
#         NAME: 'Author Person',
#         ppl.AFFILIATION: 'NYU',
#         EMAIL: non_masthead_email
#     }
#     ppl.people_dict[non_masthead_email] = non_masthead_person
#
#     # Call get_masthead to retrieve the masthead people
#     masthead = get_masthead()
#
#     # Verify that the masthead person is included
#     assert masthead_email in masthead
#     assert masthead[masthead_email][NAME] == 'Editor Person'
#
#     # Verify that the non-masthead person is not included
#     assert non_masthead_email not in masthead
#
#     # Clean up test data
#     delete_person(masthead_email)
#     delete_person(non_masthead_email)
#
#     print("Test passed: get_masthead returns correct masthead people and excludes non-masthead people.")