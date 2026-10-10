import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import database as db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = os.path.join(app.config['BASE_DIR'], 'instance', 'test_resumeready.db')
    with app.test_client() as client:
        with app.app_context():
            db.init_db()
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Analyze. Improve." in response.data
    assert b"Get Career Ready." in response.data

def test_upload_page(client):
    response = client.get('/upload')
    assert response.status_code == 200
    assert b"Upload Your Resume" in response.data

def test_try_sample_resume(client):
    response = client.get('/try_sample', follow_redirects=True)
    assert response.status_code == 200
    assert b"Analysis Dashboard" in response.data
    assert b"sample_resume.pdf" in response.data

def test_dashboard_and_history(client):
    res_dash = client.get('/dashboard')
    assert res_dash.status_code == 200

    res_hist = client.get('/history')
    assert res_hist.status_code == 200

def test_profile_page(client):
    res_prof = client.get('/profile')
    assert res_prof.status_code == 200
    assert b"Demo Student" in res_prof.data
