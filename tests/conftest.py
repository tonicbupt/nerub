# coding: utf-8

import os
import sys
import pytest
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nerub.network import rds


@pytest.fixture
def test_db(request):
    def tear_down():
        rds.flushall()
    request.addfinalizer(tear_down)
