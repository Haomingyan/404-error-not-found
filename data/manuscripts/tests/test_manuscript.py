import pytest
import data.manuscripts.manuscript as mt

TEST_TITLE = "Test Title"
TEST_AUTHOR = "Test Author"
TEST_REFEREE = "Test Referee"
TEST_AUTHOR_EMAIL = "test@nyu.edu"
TEST_TEXT = "Test Text"
TEST_ABSTRACT = "Test Abstract"
TEST_EDITOR_EMAIL = "testEditor@gmail.com"

@pytest.mark.skip(reason="Delete not implemented yet")
def test_create():
    assert not mt.exists(TEST_TITLE)
    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    assert mt.exists(TEST_TITLE)
    #mt.delete(TEST_TITLE)


@pytest.mark.skip(reason="Delete not implemented yet")
def test_read():
    # if mt.exists(TEST_TITLE):
    #     mt.delete(TEST_TITLE)
    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    manuscripts = mt.read()
    assert TEST_TITLE in manuscripts
    #mt.delete(TEST_TITLE)


@pytest.mark.skip(reason="Delete not implemented yet")
def test_read_one():
    # if mt.exists(TEST_TITLE):
    #     mt.delete(TEST_TITLE)

    mt.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL,
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    manuscript = mt.read_one(TEST_TITLE)
    assert manuscript is not None
    assert manuscript['title'] == TEST_TITLE
    #mt.delete(TEST_TITLE)
