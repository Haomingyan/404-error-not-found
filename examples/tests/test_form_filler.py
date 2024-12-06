from unittest.mock import patch

import examples.form_filler as ff


def test_get_fld_names():
    ret = ff.get_fld_names(ff.TEST_FLD_DESCRIPS)
    assert isinstance(ret, list)
    assert ff.TEST_FLD in ret


def test_get_form_descr():
    ret = ff.get_form_descr(ff.TEST_FLD_DESCRIPS)
    assert isinstance(ret, dict)
    assert ff.TEST_FLD in ret


@patch('examples.form_filler.get_input', return_value='Y')
def test_form(mock_get_input):
    assert isinstance(ff.form(ff.TEST_FLD_DESCRIPS), dict)

def test_get_query_fld_names():
    ret = ff.get_query_fld_names(ff.TEST_FLD_DESCRIPS)
    assert isinstance(ret, list)
    assert ff.TEST_FLD in ret


def test_form_default_value():
    fld_descrips = [
        {
            ff.FLD_NM: 'default_test_field',
            ff.DEFAULT: 'default_value',
            ff.PARAM_TYPE: ff.QUERY_STR,
            ff.QSTN: 'What is the default value?'
        }
    ]
    with patch('examples.form_filler.get_input', return_value='') as mock_get_input:
        ret = ff.form(fld_descrips)
        assert ret['default_test_field'] == 'default_value'

def test_get_query_fld_names():
    ret = ff.get_query_fld_names(ff.TEST_FLD_DESCRIPS)
    assert isinstance(ret, list)
    assert ff.TEST_FLD in ret

def test_form_default_value():
    fld_descrips = [
        {
            ff.FLD_NM: 'default_test_field',
            ff.DEFAULT: 'default_value',
            ff.PARAM_TYPE: ff.QUERY_STR,
            ff.QSTN: 'What is the default value?'
        }
    ]
    with patch('examples.form_filler.get_input', return_value='') as mock_get_input:
        ret = ff.form(fld_descrips)
        assert ret['default_test_field'] == 'default_value'