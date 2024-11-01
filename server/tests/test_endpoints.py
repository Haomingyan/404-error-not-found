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

import pytest
import json

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json

def test_title():
    resp = TEST_CLIENT.get(ep.TITLE_EP)
    resp_json = resp.get_json()
    assert ep.TITLE_RESP in resp_json
    assert isinstance(resp_json[ep.TITLE_RESP], str)

def test_create_person():
    person_data = {
        "name": "Test",
        "affiliation": "Test",
        "email": "testuser@example.com",
        "role": "AU"
    }

    resp = TEST_CLIENT.post(
        ep.PEOPLE_EP,
        json=person_data
    )

    assert resp.status_code == 200
    response_data = resp.get_json()
    assert response_data['Message'] == 'Person added!'

def test_create_duplicate_person():
    person_data = {
        "name": "Test",
        "affiliation": "Test",
        "email": "testuser@example.com",
        "role": "AU"
    }

    resp = TEST_CLIENT.post(
        ep.PEOPLE_EP,
        json=person_data
    )

    assert resp.status_code >= 400
    assert 'duplicate' in resp.get_json()['message']


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


def test_read_person():
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    resp_json = resp.get_json()
    for _id, person in resp_json.items():
        assert isinstance(_id, str)
        assert len(_id) > 0
        assert NAME in person

def test_delete_person():
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

    # Delete the person
    resp = TEST_CLIENT.delete(
        ep.PEOPLE_EP,
        json={"email": "deleteuser@example.com"}
    )

    assert resp.status_code == OK
    assert resp.get_json()['message'] == 'Person deleted successfully'

    # Try to delete the person again to ensure it was deleted
    resp = TEST_CLIENT.delete(
        ep.PEOPLE_EP,
        json={"email": "deleteuser@example.com"}
    )

    assert resp.status_code == NOT_FOUND
    assert resp.get_json()['message'] == 'Person not found'


def test_update_person():

    person_data = {
        "name": "Original Name",
        "affiliation": "Original Affiliation",
        "email": "updateuser@example.com",
        "role": "author"
    }

    resp = TEST_CLIENT.post(
        ep.PEOPLE_EP,
        json=person_data
    )
    assert resp.status_code == 200

    updated_data = {
        "name": "Updated Name",
        "affiliation": "Updated Affiliation",
        "email": "updateuser@example.com",
        "role": "editor"
    }

    resp = TEST_CLIENT.put(
        ep.PEOPLE_EP,
        json=updated_data
    )

    assert resp.status_code == 200
    resp_json = resp.get_json()
    assert resp_json['Message'] == 'Person updated successfully'
    assert resp_json['return']['name'] == "Updated Name"
    assert resp_json['return']['affiliation'] == "Updated Affiliation"
    assert "editor" in resp_json['return']['roles']

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

    # Delete the text entry
    resp = TEST_CLIENT.delete(
        ep.TEXT_EP,
        json={"key": "delete_test"}
    )

    assert resp.status_code == OK
    assert resp.get_json()['message'] == 'Text deleted successfully'

    # Try to delete the text entry again to ensure it was deleted
    resp = TEST_CLIENT.delete(
        ep.TEXT_EP,
        json={"key": "delete_test"}
    )

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


