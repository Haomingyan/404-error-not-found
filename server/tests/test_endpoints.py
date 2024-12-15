from http import HTTPStatus
from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch
from data.people import NAME
import data.manuscripts.manuscript as mt

import pytest
import json

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

TEST_TITLE = "Test Manuscript"
TEST_AUTHOR = "Test Author"
TEST_AUTHOR_EMAIL = "test_author@example.com"
TEST_TEXT = "Original Text"
TEST_ABSTRACT = "Original Abstract"
TEST_EDITOR_EMAIL = "editor@example.com"

@patch("server.endpoints.HELLO_RESP", "Hello, patched response!")
def test_hello_with_patch():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert "Hello, patched response!" in resp_json

def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json

def test_title():
    resp = TEST_CLIENT.get(ep.TITLE_EP)
    resp_json = resp.get_json()
    assert ep.TITLE_RESP in resp_json
    assert isinstance(resp_json[ep.TITLE_RESP], str)

# def test_create_person():
#     person_data = {
#         "name": "Test",
#         "affiliation": "Test",
#         "email": "testuser@example.com",
#         "role": "AU"
#     }
#
#     resp = TEST_CLIENT.post(
#         ep.PEOPLE_EP,
#         json=person_data
#     )
#
#     assert resp.status_code == 200
#     response_data = resp.get_json()
#     assert response_data['Message'] == 'Person added!'
# Fixture for person data
@pytest.fixture
def person_data():
    return {
        "name": "Test",
        "affiliation": "Test",
        "email": "newtestuser4@example.com",
        "role": "AU"
    }

# Modified test_create_person to use fixture
def test_create_person(person_data):
    try:
        # Create a new person
        resp = TEST_CLIENT.post(
            ep.PEOPLE_EP,
            json=person_data
        )
        assert resp.status_code == OK
        response_data = resp.get_json()
        assert response_data['Message'] == 'Person added!'

        # Check if the resource exists
        print("POST Response Data:", response_data)
    finally:
        # Delete the created person
        delete_resp = TEST_CLIENT.delete(
            ep.PEOPLE_EP,
            json={"email": "newtestuser4@example.com"}
        )
        print("DELETE Response:", delete_resp.get_json())
        assert delete_resp.status_code == OK, f"Cleanup failed: {delete_resp.get_json()}"


def test_create_duplicate_person(person_data):
    try:
        # Step 1: Create the first person
        first_resp = TEST_CLIENT.post(
            ep.PEOPLE_EP,
            json=person_data
        )
        assert first_resp.status_code == OK
        first_response_data = first_resp.get_json()
        assert first_response_data['Message'] == 'Person added!'
        print("First Creation Response Data:", first_response_data)

        # Step 2: Attempt to create the same person again
        duplicate_resp = TEST_CLIENT.post(
            ep.PEOPLE_EP,
            json=person_data
        )
        assert duplicate_resp.status_code == 406
        duplicate_response_data = duplicate_resp.get_json()
        print("Duplicate Creation Response Data:", duplicate_response_data)
    finally:
        # Cleanup: Delete the created person
        delete_resp = TEST_CLIENT.delete(
            ep.PEOPLE_EP,
            json={"email": person_data["email"]}
        )
        print("DELETE Response:", delete_resp.get_json())
        assert delete_resp.status_code == OK, f"Cleanup failed: {delete_resp.get_json()}"


def test_get_texts():
    # Make a GET request to the /texts endpoint
    resp = TEST_CLIENT.get(ep.TEXT_EP)

    # Check the response status code
    assert resp.status_code == OK

    # Convert the response data to JSON
    resp_json = resp.get_json()

    # Verify that the response contains the text entries
    assert isinstance(resp_json, dict)  # Ensure we get a dictionary of texts

    # Check that at least one text entry exists in the response (if texts exist)
    if resp_json:
        for key, text_entry in resp_json.items():
            assert 'title' in text_entry
            assert 'text' in text_entry
            assert isinstance(text_entry['title'], str)
            assert isinstance(text_entry['text'], str)


@patch('data.people.read', autospec=True,
       return_value={'id': {NAME: 'Joe Schmoe'}})
def test_read(mock_read):
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    for _id, person in resp_json.items():
        assert isinstance(_id, str)
        assert len(_id) > 0
        assert NAME in person

@patch('data.people.read', autospec=True, return_value={})
def test_read_nonexistent_person(mock_read):
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    
    non_existent_id = "nonexistent_id"
    assert non_existent_id not in resp_json, f"Unexpected ID: {non_existent_id}"
    assert resp_json == {}, "Response should be empty for nonexistent person"
    

@patch("data.people.delete_person", autospec=True, return_value=True)
def test_delete_person(mock_delete):
    person_data = {
        "name": "Delete Test",
        "affiliation": "Test",
        "email": "deleteuser@example.com"
    }

    # Create the person to be deleted
    TEST_CLIENT.post(
        ep.PEOPLE_EP,
        json=person_data
    )

    # Delete the person (mocking the delete function)
    resp = TEST_CLIENT.delete(
        ep.PEOPLE_EP,
        json={"email": "deleteuser@example.com"}
    )

    assert resp.status_code == OK
    assert resp.get_json()['message'] == 'Person deleted successfully'
    mock_delete.assert_called_once_with("deleteuser@example.com")

    # Try to delete the person again to ensure it was deleted
    mock_delete.return_value = False  # Simulate that the person no longer exists
    resp = TEST_CLIENT.delete(
        ep.PEOPLE_EP,
        json={"email": "deleteuser@example.com"}
    )

    assert resp.status_code == NOT_FOUND
    assert resp.get_json()['message'] == 'Person not found'



# def test_delete_person():
#     person_data = {
#         "name": "Delete Test",
#         "affiliation": "Test",
#         "email": "deleteuser@example.com"
#     }
#
#     # Create the person to be deleted
#     TEST_CLIENT.post(
#         ep.PEOPLE_EP,
#         json=person_data
#     )
#
#     # Delete the person
#     resp = TEST_CLIENT.delete(
#         ep.PEOPLE_EP,
#         json={"email": "deleteuser@example.com"}
#     )
#
#     assert resp.status_code == OK
#     assert resp.get_json()['message'] == 'Person deleted successfully'
#
#     # Try to delete the person again to ensure it was deleted
#     resp = TEST_CLIENT.delete(
#         ep.PEOPLE_EP,
#         json={"email": "deleteuser@example.com"}
#     )
#
#     assert resp.status_code == NOT_FOUND
#     assert resp.get_json()['message'] == 'Person not found'

@pytest.fixture
def update_person_data():
    return {
        "name": "Original Name",
        "affiliation": "Original Affiliation",
        "email": "updateuser@example.com",
        "role": "author"
    }

@pytest.fixture
def non_existent_person_data():
    return {
        "name": "Nonexistent Person",
        "affiliation": "Unknown",
        "email": "nonexistent@example.com",
        "role": "author"
    }

def test_update_nonexistent_person(non_existent_person_data):
    resp = TEST_CLIENT.put(
        ep.PEOPLE_EP,
        json=non_existent_person_data
    )


@patch('data.people.update_person', autospec=True, return_value={
    'id': '1234',
    'name': 'Updated Name',
    'affiliation': 'Updated Affiliation',
    'email': 'updateuser@example.com',
    'roles': ['editor']
})
def test_update(mock_update):
    update_data = {
        "id": "1234",
        "name": "Updated Name",
        "affiliation": "Updated Affiliation",
        "email": "updateuser@example.com",
        "role": "editor"
    }
    resp = TEST_CLIENT.put(
        ep.PEOPLE_EP,
        json=update_data
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json['Message'] == 'Person updated successfully'
    mock_update.assert_called_once_with(
        "Updated Name",
        "Updated Affiliation",
        "updateuser@example.com",
        "editor"
    )


def test_create_text():
    text_data = {
        "key": "001",
        "title": "Ocean Exploration",
        "text": "This text is about exploring the ocean depths."
    }

    resp = TEST_CLIENT.post(
        ep.TEXT_EP,
        json=text_data
    )

    assert resp.status_code == 201
    assert resp.get_json()['message'] == 'Text created successfully'

def test_create_duplicate_text():
    text_data = {
        "key": "001",
        "title": "Ocean Exploration",
        "text": "This text is about exploring the ocean depths."
    }

    # First creation should succeed
    TEST_CLIENT.post(
        ep.TEXT_EP,
        json=text_data
    )

    # Attempt to create the same text entry again
    resp = TEST_CLIENT.post(
        ep.TEXT_EP,
        json=text_data
    )

    assert resp.status_code == 400
    assert 'already exists' in resp.get_json()['message']

def test_delete_text():
    text_data = {
        "key": "delete_test",
        "title": "Delete Test",
        "text": "This text is for testing delete functionality."
    }

    # Create the text entry to be deleted
    TEST_CLIENT.post(
        ep.TEXT_EP,
        json=text_data
    )

    # Delete the text entry using the path parameter
    resp = TEST_CLIENT.delete(f"/text/{text_data['key']}")
    assert resp.status_code == OK
    assert resp.get_json()['message'] == 'Text deleted successfully'

    # Try to delete the text entry again to ensure it was deleted
    resp = TEST_CLIENT.delete(f"/text/{text_data['key']}")
    assert resp.status_code == NOT_FOUND
    assert resp.get_json()['message'] == 'Text entry not found'


def test_update_text():
    # Initial text data
    text_data = {
        "key": "update_test",
        "title": "Original Title",
        "text": "This is the original text."
    }

    # Create the text entry to be updated
    resp = TEST_CLIENT.post(
        ep.TEXT_EP,
        json=text_data
    )
    assert resp.status_code == 201

    # Updated text data
    updated_data = {
        "key": "update_test",
        "title": "Updated Title",
        "text": "This text has been updated."
    }

    # Update the text entry
    resp = TEST_CLIENT.put(
        ep.TEXT_EP,
        json=updated_data
    )
    assert resp.status_code == 200
    resp_json = resp.get_json()
    assert resp_json['message'] == 'Text updated successfully'
    assert resp_json['text']['title'] == "Updated Title"
    assert resp_json['text']['text'] == "This text has been updated."

@pytest.mark.skip(reason="Skipping endpoint test temporarily")
def test_endpoints(test_client):
    """
    Test the /endpoints endpoint to ensure it returns all available endpoints.
    """
    response = test_client.post(ep.ENDPOINT_EP)
    assert response.status_code == 200
    resp_json = response.get_json()
    assert "Available endpoints" in resp_json
    assert isinstance(resp_json["Available endpoints"], list)
    assert len(resp_json["Available endpoints"]) > 0

TEST_TITLE = "Test Title"
TEST_EMAIL = "test@nyu.edu"
MANUSCRIPT_DATA = {
    mt.TITLE: "Test Manuscript",
    mt.AUTHOR: "Test Author",
    mt.AUTHOR_EMAIL: TEST_EMAIL,
    mt.TEXT: "Test Text",
    mt.ABSTRACT: "Test Abstract",
    mt.EDITOR_EMAIL: TEST_EMAIL
}

def test_delete_manuscript():
    title = "Test Manuscript Delete"
    author = "John Doe"
    author_email = "john.doe@example.com"
    text = "This is the body of the test manuscript to delete."
    abstract = "A brief summary of the test manuscript for deletion."
    editor_email = "editor@example.com"

    manuscript_data = {
        "title": title,
        "author": author,
        "author_email": author_email,
        "text": text,
        "abstract": abstract,
        "editor_email": editor_email,
        "referees": {
            "referee_email@example.com": {
                "report": "Good paper",
                "verdict": "ACCEPT"
            }
        }
    }

    if mt.exists(title):
        mt.delete(title)

    # Create the manuscript
    resp_create = TEST_CLIENT.post(f'{MANUSCRIPT_EP}/create', json=manuscript_data)
    assert resp_create.status_code == HTTPStatus.OK, f"Creation failed: {resp_create.get_json()}"
    response_create_data = resp_create.get_json()
    assert response_create_data['Message'] == 'Manuscript added!'
    assert response_create_data['return'] == title

    # Delete the manuscript
    resp_delete = TEST_CLIENT.delete(f'{MANUSCRIPT_EP}/delete', json={"title": title})
    assert resp_delete.status_code == HTTPStatus.OK, f"Delete failed: {resp_delete.get_json()}"
    response_delete_data = resp_delete.get_json()
    assert 'deleted successfully' in response_delete_data['Message']
    assert response_delete_data['return'] == title

    # Attempt to delete the manuscript again to ensure it was removed
    resp_delete_again = TEST_CLIENT.delete(f'{MANUSCRIPT_EP}/delete', json={"title": title})
    assert resp_delete_again.status_code == HTTPStatus.NOT_FOUND, f"Should not find manuscript: {resp_delete_again.get_json()}"
    response_delete_again_data = resp_delete_again.get_json()
    assert 'does not exist' in response_delete_again_data['Message']



MANUSCRIPT_EP = '/manuscript'


def test_create_manuscript():
    if mt.exists(MANUSCRIPT_DATA[mt.TITLE]):
        mt.delete(MANUSCRIPT_DATA[mt.TITLE])
    manuscript_data = {
        "title": "Test Manuscript",
        "author": "John Doe",
        "author_email": "john.doe@example.com",
        "text": "This is the body of the test manuscript.",
        "abstract": "A brief summary of the test manuscript.",
        "editor_email": "editor@example.com",
        "referees": {
            "referee_email@example.com": {
                "report": "Good paper",
                "verdict": "ACCEPT"
            }
        }
    }

    resp = TEST_CLIENT.post(f'{MANUSCRIPT_EP}/create', json=manuscript_data)
    assert resp.status_code == HTTPStatus.OK
    response_data = resp.get_json()
    assert response_data['Message'] == 'Manuscript added!'
    assert response_data['return'] == manuscript_data['title']

@pytest.fixture
def create_test_manuscript():
    # Ensure manuscript does not exist
    if mt.exists(TEST_TITLE):
        mt.delete(TEST_TITLE)
    # Create a fresh manuscript for testing
    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    yield
    # Cleanup after test
    if mt.exists(TEST_TITLE):
        mt.delete(TEST_TITLE)

def test_update_manuscript(create_test_manuscript):
    # Verify that the manuscript was created
    manuscript = mt.read_one(TEST_TITLE)
    assert manuscript is not None
    assert manuscript[mt.TITLE] == TEST_TITLE
    assert manuscript[mt.AUTHOR] == TEST_AUTHOR
    assert manuscript[mt.AUTHOR_EMAIL] == TEST_AUTHOR_EMAIL
    assert manuscript[mt.TEXT] == TEST_TEXT
    assert manuscript[mt.ABSTRACT] == TEST_ABSTRACT
    assert manuscript[mt.EDITOR_EMAIL] == TEST_EDITOR_EMAIL

    # Prepare updated data as a dict
    updates = {
        mt.AUTHOR: "Updated Author",
        mt.AUTHOR_EMAIL: "updated_author@example.com",
        mt.TEXT: "Updated Text of the manuscript.",
        mt.ABSTRACT: "Updated Abstract",
        mt.EDITOR_EMAIL: "updated_editor@example.com"
    }

    # Perform the update
    updated_manuscript = mt.update(TEST_TITLE, updates)
    assert updated_manuscript is not None
    assert updated_manuscript[mt.AUTHOR] == "Updated Author"
    assert updated_manuscript[mt.AUTHOR_EMAIL] == "updated_author@example.com"
    assert updated_manuscript[mt.TEXT] == "Updated Text of the manuscript."
    assert updated_manuscript[mt.ABSTRACT] == "Updated Abstract"
    assert updated_manuscript[mt.EDITOR_EMAIL] == "updated_editor@example.com"