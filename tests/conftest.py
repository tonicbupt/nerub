# coding: utf-8

import pytest
from nerub.network import rds


@pytest.fixture
def test_db(request):
    def tear_down():
        rds.flushall()
    request.addfinalizer(tear_down)
