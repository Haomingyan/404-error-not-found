import data.manuscripts.query as mqry

def test_is_valid_state():
    for state in mqry.get_states():
        assert mqry.is_valid_state(state)
    