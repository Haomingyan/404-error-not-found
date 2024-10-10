import data.users as usrs
import data.people as ppl

def test_read():
    users = usrs.get_users()
    assert isinstance(users, dict)
    assert len(users) > 0  # at least one user!
    for key in users:
        assert isinstance(key, str)
        assert len(key) >= usrs.MIN_USER_NAME_LEN
        user = users[key]
        assert isinstance(user, dict)
        assert usrs.LEVEL in user
        assert isinstance(user[usrs.LEVEL], int)

def test_delete_person():
    # Test deleting an existing person
    people = ppl.read()
    assert ppl.DEL_EMAIL in people
    deleted_person = ppl.delete_person(ppl.DEL_EMAIL)
    assert deleted_person == ppl.DEL_EMAIL
    updated_people = ppl.read()
    assert ppl.DEL_EMAIL not in updated_people

    # Test deleting a non-existing person
    non_existing_email = 'nonexistent@nyu.edu'
    deleted_person = ppl.delete_person(non_existing_email)
    assert deleted_person is None
