import os
import sys
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from main import app

client = TestClient(app)


def test_root_alive():
    """API root should respond."""
    res = client.get("/")
    assert res.status_code == 200


def test_get_screenings_list():
    """
    Basic test for the screenings list endpoint.
    It checks the endpoint works and returns a list.
    """
    res = client.get("/screenings/")
    assert res.status_code == 200

    data = res.json()
    assert isinstance(data, list)


def test_screenings_filter_by_hall_and_date():
    """
    Testing  the core feature:
    Selecting a hall + date returns screenings
    """
    params = {"hall_id": 1, "show_date": "2024-01-01"}
    res = client.get("/screenings/", params=params)
    
    assert res.status_code == 200

    data = res.json()
    assert isinstance(data, list)
