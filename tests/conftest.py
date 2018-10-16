from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from sqlbag import temporary_database


@pytest.yield_fixture(scope="module")
def db():
    with temporary_database() as dburi:
        yield dburi
