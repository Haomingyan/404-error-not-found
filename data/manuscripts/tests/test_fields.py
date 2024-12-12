import data.manuscripts.fields as mflds

def test_get_flds():
    assert isinstance(mflds.get_flds(), dict)

def test_get_fld_names():
    # Check that get_fld_names returns a list of field names (strings)
    fld_names = mflds.get_fld_names()
    assert isinstance(fld_names, list), "get_fld_names() should return a list"
    assert all(isinstance(name, str) for name in fld_names), "All field names should be strings"

def test_get_disp_name():
    # Check that get_disp_name returns the correct display name for a known field
    display_name = mflds.get_disp_name(mflds.TEST_FLD_NM)
    assert isinstance(display_name, str), "get_disp_name() should return a string"
    assert display_name == mflds.TEST_FLD_DISP_NM, "get_disp_name() should return the expected display name"