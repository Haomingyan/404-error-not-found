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
    # Step 1: 创建一个用户
    person_data = {
        "name": "Original Name",
        "affiliation": "Original Affiliation",
        "email": "updateuser@example.com"
    }

    # 创建用户
    resp = TEST_CLIENT.post(
        ep.PEOPLE_EP,
        json=person_data
    )
    assert resp.status_code == 201

    # Step 2: 更新用户信息
    updated_data = {
        "name": "Updated Name",
        "affiliation": "Updated Affiliation",
        "email": "updateuser@example.com"
    }

    resp = TEST_CLIENT.put(
        ep.PEOPLE_EP,
        json=updated_data
    )

    # 验证更新结果
    assert resp.status_code == 200
    resp_json = resp.get_json()
    assert resp_json['message'] == 'Person updated successfully'
    assert resp_json['person']['name'] == "Updated Name"
    assert resp_json['person']['affiliation'] == "Updated Affiliation"


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

