import pytest
import data.text as txt


def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    for key in texts:
        assert isinstance(key, str)

def test_create_text():
    new_key = 'NewPage'
    title = 'New Page Title'
    text_content = 'This is the content for the new page.'

    created_text = txt.create_text(new_key, title, text_content)

    assert new_key in txt.text_dict
    assert txt.text_dict[new_key][txt.TITLE] == title
    assert txt.text_dict[new_key][txt.TEXT] == text_content

def test_create_duplicate_text():
    duplicate_key = txt.HOMEPAGE_KEY
    title = 'Duplicate Title'
    text_content = 'This should raise an error.'

    with pytest.raises(ValueError) as exc_info:
        txt.create_text(duplicate_key, title, text_content)

    assert str(exc_info.value) == f'Text with key "{duplicate_key}" already exists.'


def test_delete_text():
    # First, ensure the key exists
    key_to_delete = 'NewPage'
    assert key_to_delete in txt.text_dict

    # Delete the text and check it is removed
    delete_message = txt.delete_text(key_to_delete)
    assert delete_message == {"message": f"Text with key '{key_to_delete}' has been deleted."}
    assert key_to_delete not in txt.text_dict

def test_delete_nonexistent_text():

    nonexistent_key = 'NonexistentPage'
    with pytest.raises(ValueError) as exc_info:
        txt.delete_text(nonexistent_key)

    assert str(exc_info.value) == f'Text with key "{nonexistent_key}" does not exist.'

def test_update_text():
    new_key = txt.HOMEPAGE_KEY
    new_title = 'Updated Page Title'
    new_text = 'This is the updated content'

    updated_text = txt.update_text(new_key, new_title, new_text)

    assert updated_text[txt.TITLE] == new_title
    assert updated_text[txt.TEXT] == new_text
    assert txt.text_dict[new_key][txt.TITLE] == new_title
    assert txt.text_dict[new_key][txt.TEXT] == new_text

def test_update_nonexistent_text():
    nonexistent_key = 'Non-existent Page'
    new_title = 'New title'
    new_text = 'New content for a page that does not exist'

    with pytest.raises(ValueError) as exc_info:
        txt.update_text(nonexistent_key,new_title,new_text)
        
    assert str(exc_info.value) == f'Text with key "{nonexistent_key}" does not exist.'


def test_read_one():
    assert len(txt.read_one(txt.HOMEPAGE_KEY)) > 0

def test_read_one_not_found():
    assert txt.read_one('Not a page key!') == {}

