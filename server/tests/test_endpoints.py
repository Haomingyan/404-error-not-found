from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

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
        "email": "testuser@example.com"
    }

    resp = TEST_CLIENT.post(
        ep.PEOPLE_EP,
        json=person_data
    )

    assert resp.status_code == 201
    assert resp.get_json()['message'] == 'Person created successfully'

def test_create_duplicate_person():
    person_data = {
        "name": "Test",
        "affiliation": "Test",
        "email": "testuser@example.com"
    }

    resp = TEST_CLIENT.post(
        ep.PEOPLE_EP,
        json=person_data
    )

    assert resp.status_code == BAD_REQUEST
    assert 'duplicate' in resp.get_json()['message']

def test_read_person():
    person_data = {
        "name": "test_name",
        "affiliation":"test_affiliation",
        "email": "testuser@nyu.edu"
    }

    TEST_CLIENT.post(
        ep.PEOPLE_EP,
        json = person_data
    )

    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert isinstance(resp_json, list)
    assert len(resp_json) > 0
    assert resp_json[0]['name'] == "test_name"
    assert resp_json[0]['affiliation'] == "test_affiliation"
    assert resp_json[0]['email'] == "testuser@nyu.edu"

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