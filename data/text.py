"""
This module interfaces to our user data.
"""

# fields
KEY = 'key'
TITLE = 'title'
TEXT = 'text'
EMAIL = 'email'

TEST_KEY = 'HomePage'
DEL_KEY = 'DeletePage'

text_dict = {
    TEST_KEY: {
        TITLE: 'Home Page',
        TEXT: 'This is a journal about building API servers.',
    },
    # DEL_KEY: {
    #     TITLE: 'Home Page',
    #     TEXT: 'This is a journal about building API servers.',
    #},
}


def read():  # test function added
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    text = text_dict
    return text


def create_text(key, title, text):  # test function added
    """
    Create a new text entry in text_dict.
    - key: A unique identifier for the text
    - title: The title of the page.
    - text: The content of the page.
    """
    if key in text_dict:
        raise ValueError(f'Text with key "{key}" already exists.')

    text_dict[key] = {
        TITLE: title,
        TEXT: text
    }
    return text_dict[key]


def update_text(key, title, text):  # test function added
    if key not in text_dict:
        raise ValueError(f'Text with key "{key}" does not exist.')
    else:
        text_dict[key] = {
            TITLE: title,
            TEXT: text
        }
    return text_dict[key]


def delete_text(key):
    """
    Delete an existing text entry from text_dict.
    """
    global text_dict
    if key not in text_dict:
        raise ValueError(f'Text with key "{key}" does not exist.')

    del text_dict[key]
    return {"message": f"Text with key '{key}' has been deleted."}


def read_one(key: str) -> dict:
    # This should take a key and return the page dictionary
    # for that key. Return an empty dictionary of key not found.
    result = {}
    if key in text_dict:
        result = text_dict[key]
    return result


def main():
    print(read())


if __name__ == '__main__':
    main()
