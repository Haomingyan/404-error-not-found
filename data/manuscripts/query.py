# states:
AUTHOR_REV = 'AUR'
COPY_EDIT = 'CED'
IN_REF_REV = 'REV'
REJECTED = 'REJ'
SUBMITTED = 'SUB'
TEST_STATE = SUBMITTED

VALID_STATES = [
    COPY_EDIT,
    IN_REF_REV,
    REJECTED,
    SUBMITTED,
]


def get_states() -> list:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


ACCEPT = 'ACC'
ASSIGN_REF = 'ARF'
DONE = 'DON'
REJECT = 'REJ'

VALID_ACTIONS = [
    ACCEPT,
    ASSIGN_REF,
    DONE,
    REJECT
]


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


FUNC = 'f'

STATE_TABLE = {
    SUBMITTED: {
        ASSIGN_REF: {
            # These next lines are alternatives that work the same.
            # FUNC: sub_assign_ref,
            FUNC: lambda m: IN_REF_REV,
        },
        REJECT: {
            FUNC: lambda m: REJECTED,
        },
    },
    IN_REF_REV: {
    },
    COPY_EDIT: {
        DONE: {
            FUNC: lambda m: AUTHOR_REV,
        },
    },
    AUTHOR_REV: {
    },
    REJECTED: {
    },
}


def get_valid_actions_by_state(state: str):
    valid_actions = STATE_TABLE[state].keys()
    print(f'{valid_actions=}')
    return valid_actions

def handle_action(curr_state, action, manuscript) -> str:
    if curr_state not in STATE_TABLE:
        raise ValueError(f'Bad state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'{action} not available in {curr_state}')
    return STATE_TABLE[curr_state][action][FUNC](manuscript)