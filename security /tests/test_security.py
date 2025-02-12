from .. import security as sec


def test_read():
    recs = sec.read()
    assert isinstance(recs, dict)
    for feature in recs:
        assert isinstance(feature, str)
        assert len(feature) > 0


def test_read_feature_people():
    """
    Test that read_feature can retrieve the PEOPLE feature
    and that it has the expected structure.
    """
    # Make sure data is loaded first
    sec.read()

    # Now call read_feature
    people_data = sec.read_feature(sec.PEOPLE)

    # Check the result is a dict
    assert isinstance(people_data, dict), "PEOPLE feature should be a dictionary"

    # Example of checking if it has a CREATE key or something else
    assert sec.CREATE in people_data, "PEOPLE feature should have a CREATE key"
    assert isinstance(people_data[sec.CREATE], dict), "CREATE should map to a dict"

    # Optionally, you can check the user_list or checks subfields
    create_data = people_data[sec.CREATE]
    assert sec.USER_LIST in create_data, "CREATE should have a USER_LIST"
    assert sec.CHECKS in create_data, "CREATE should have a CHECKS dictionary"