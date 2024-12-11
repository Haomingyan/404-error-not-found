"""
This module provides a sample query form.
"""

import backendcore.data.form_filler as ff

from templates.fields import CODE

FORM_FLDS = [
    {
        ff.FLD_NM: CODE,
        ff.QSTN: 'Sample:',
        ff.PARAM_TYPE: ff.QUERY_STR,
    },
]


def get_form() -> list:
    return FORM_FLDS