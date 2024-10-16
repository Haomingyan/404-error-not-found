import pytest
import data.text as txt

def test_create_text():
    new_key = 'NewPage'
    title = 'New Page Title'
    text_content = 'This is the content for the new page.'

    created_text = txt.create_text(new_key, title, text_content)

    assert new_key in txt.text_dict
    assert txt.text_dict[new_key][txt.TITLE] == title
    assert txt.text_dict[new_key][txt.TEXT] == text_content

def test_create_duplicate_text():
    duplicate_key = txt.TEST_KEY
    title = 'Duplicate Title'
    text_content = 'This should raise an error.'

    with pytest.raises(ValueError) as exc_info:
        txt.create_text(duplicate_key, title, text_content)

    assert str(exc_info.value) == f'Text with key "{duplicate_key}" already exists.'


def test_delete_text():
    # First, ensure the key exists
    key_to_delete = txt.DEL_KEY
    assert key_to_delete in txt.text_dict

    # Delete the text and check it is removed
    delete_message = txt.delete_text(key_to_delete)
    assert delete_message == f'Text with key "{key_to_delete}" has been deleted.'
    assert key_to_delete not in txt.text_dict

def test_delete_nonexistent_text():

    nonexistent_key = 'NonexistentPage'
    with pytest.raises(ValueError) as exc_info:
        txt.delete_text(nonexistent_key)

    assert str(exc_info.value) == f'Text with key "{nonexistent_key}" does not exist.'
