"""
Unit Testing for Screening

These tests verify:
- The root endpoint is reachable
- Screenings list endpoint returns a valid response
- Screenings can be filtered by hall and date
"""

import os
import sys
from fastapi.testclient import TestClient

# Environment Setup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from main import app

client = TestClient(app)


# Root Endpoint Test

def test_root_alive():
    """root should respond to pass"""
    res = client.get("/")
    assert res.status_code == 200


# Screenings List Test

def test_get_screenings_list():
    """It checks that the Screening endpoint works and returns a list"""
    
    res = client.get("/screenings/")
    assert res.status_code == 200

    data = res.json()
    assert isinstance(data, list)


# Screening Filtering Test

def test_screenings_filter_by_hall_and_date():
    """ Testing for selecting a hall and  date returns screenings"""
    
    params = {"hall_id": 1, "show_date": "2024-01-01"}
    res = client.get("/screenings/", params=params)
    
    assert res.status_code == 200

    data = res.json()
    assert isinstance(data, list)
