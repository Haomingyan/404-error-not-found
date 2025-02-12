import data.db_connect as dbc
import data.people as ppl
import data.manuscripts.query as qy

# Required Fields
TITLE = 'title'
AUTHOR = 'author'
AUTHOR_EMAIL = 'author_email'
STATE = 'state'
REFEREES = 'referees'
TEXT = 'text'
ABSTRACT = 'abstract'
HISTORY = 'history'
EDITOR_EMAIL = 'editor_email'
MANUSCRIPTS_COLLECT = 'manuscripts'
ACTION = 'action'
def read() -> dict:
    """
    return all the manuscripts
    """
    manuscripts = dbc.read_dict(MANUSCRIPTS_COLLECT, TITLE)
    return manuscripts


def read_one(title: str) -> dict:
    """
    return a specific manuscript
    """
    return dbc.read_one(MANUSCRIPTS_COLLECT, {TITLE: title})

def exists(title: str) -> bool:
    """
    Check if a manuscript exist
    """
    return read_one(title) is not None

def is_valid_manuscript(title: str, author: str,
                        author_email: str, text: str,
                        abstract: str, editor_email: str) -> bool:
    if not ppl.is_valid_email(author_email):
        raise ValueError(f'Author email invalid: {author_email}')
    if not ppl.is_valid_email(editor_email):
        raise ValueError(f'Editor email invalid: {editor_email}')
    if not title.strip():
        raise ValueError("Title cannot be blank")
    if not author.strip():
        raise ValueError("Author cannot be blank")
    if not text.strip():
        raise ValueError("Text cannot be blank")
    if not abstract.strip():
        raise ValueError("Abstract cannot be blank")
    return True

def create(title: str, author: str, author_email: str,
           text: str, abstract: str, editor_email: str):
    if exists(title):
        raise ValueError(f"Manuscript with {title=} already exists.")
    if is_valid_manuscript(title, author, author_email, text,
                           abstract, editor_email):
        manuscript = {
            TITLE: title,
            AUTHOR: author,
            AUTHOR_EMAIL: author_email,
            STATE: qy.SUBMITTED,
            REFEREES: [],
            TEXT: text,
            ABSTRACT: abstract,
            HISTORY: [qy.SUBMITTED],
            EDITOR_EMAIL: editor_email,
        }
        dbc.create(MANUSCRIPTS_COLLECT, manuscript)
        return title

def update(title: str, updates: dict) -> dict:
    if not title.strip():
        raise ValueError("Title cannot be blank")
    manuscript = read_one(title)
    if not manuscript:
        raise ValueError(f"Manuscript with title '{title}' does not exist.")
    if TITLE in updates:
        del updates[TITLE]
    if AUTHOR_EMAIL in updates and not ppl.is_valid_email(updates[AUTHOR_EMAIL]):
        raise ValueError(f'Invalid author email: {updates[AUTHOR_EMAIL]}')
    if EDITOR_EMAIL in updates and not ppl.is_valid_email(updates[EDITOR_EMAIL]):
        raise ValueError(f'Invalid editor email: {updates[EDITOR_EMAIL]}')

    dbc.update_doc(MANUSCRIPTS_COLLECT, {TITLE: title}, updates)

    return read_one(title)


def delete(title: str) -> bool:
    if not title.strip():
        raise ValueError("Title cannot be blank")
    manuscript = read_one(title)
    if not manuscript:
        raise ValueError(f"Manuscript with title '{title}' does not exist.")

    dbc.delete(MANUSCRIPTS_COLLECT, {TITLE: title})
    return True
def update_state(title: str, action: str, **kwargs):
    manuscript = read_one(title)
    current_state = manuscript[STATE]
    # Determine the new state using handle_action
    new_state = qy.handle_action(
        current_state, action, title=title, **kwargs
    )
    # Update the manuscript state and history in the database
    dbc.update_doc(
        MANUSCRIPTS_COLLECT,
        {TITLE: title},
        {
            STATE: new_state,
            HISTORY: manuscript[HISTORY] + [new_state],
        },
    )
    return title

