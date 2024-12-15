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