import pytest
import data.manuscripts.manuscript as mt

TEST_TITLE = "Test Title"
TEST_AUTHOR = "Test Author"
TEST_REFEREE = "Test Referee"
TEST_AUTHOR_EMAIL = "test@nyu.edu"
TEST_TEXT = "Test Text"
TEST_ABSTRACT = "Test Abstract"
TEST_EDITOR_EMAIL = "testEditor@gmail.com"

def test_create():
    assert not mt.exists(TEST_TITLE)
    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    assert mt.exists(TEST_TITLE)
    mt.delete(TEST_TITLE)


def test_read():
    if mt.exists(TEST_TITLE):
        mt.delete(TEST_TITLE)
    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    manuscripts = mt.read()
    assert TEST_TITLE in manuscripts
    mt.delete(TEST_TITLE)



def test_read_one():
    if mt.exists(TEST_TITLE):
        mt.delete(TEST_TITLE)

    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    manuscript = mt.read_one(TEST_TITLE)
    assert manuscript is not None
    assert manuscript['title'] == TEST_TITLE
    mt.delete(TEST_TITLE)

@pytest.mark.skip(reason="Delete not implemented yet")
def test_update():
    # Ensure the manuscript does not exist initially
    # if mt.exists(TEST_TITLE):
    #     mt.delete(TEST_TITLE)

    # Create a new manuscript
    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    # Verify creation
    assert mt.exists(TEST_TITLE)

    # Define updates
    new_author = "Updated Author"
    new_abstract = "Updated Abstract"
    updates = {
        "author": new_author,
        "abstract": new_abstract
    }

    # Perform update
    updated_manuscript = mt.update(TEST_TITLE, updates)

    # Check if updates took place
    assert updated_manuscript is not None
    assert updated_manuscript['author'] == new_author
    assert updated_manuscript['abstract'] == new_abstract

    # Check the manuscript directly via read_one
    manuscript_after_update = mt.read_one(TEST_TITLE)
    assert manuscript_after_update['author'] == new_author
    assert manuscript_after_update['abstract'] == new_abstract

    #mt.delete(TEST_TITLE)

def test_delete():
    if mt.exists(TEST_TITLE):
        mt.delete(TEST_TITLE)

    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    assert mt.exists(TEST_TITLE)

    result = mt.delete(TEST_TITLE)
    assert result is True
    assert not mt.exists(TEST_TITLE)
