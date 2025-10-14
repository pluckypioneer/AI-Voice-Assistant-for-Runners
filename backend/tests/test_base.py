import pytest
from app.main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test the health check endpoint returns success and status running."""
    rv = client.get('/api/v1/health')
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['success'] is True
    assert body['data']['status'] == 'running'


def test_user_data_valid(client):
    """Test posting valid user data returns success."""
    payload = {"user_id": "u1", "data_type": "score", "value": 12.5}
    rv = client.post('/api/v1/user/data', json=payload)
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['success'] is True
    assert body['data']['message'] == 'Data received successfully'


def test_user_data_invalid_type(client):
    """Test posting invalid user data type returns 400."""
    payload = {"user_id": "u1", "data_type": "score", "value": "hello"}
    rv = client.post('/api/v1/user/data', json=payload)
    assert rv.status_code == 400
    body = rv.get_json()
    assert body['success'] is False


def test_user_data_missing_json(client):
    """Test missing JSON body returns 400."""
    rv = client.post('/api/v1/user/data')
    assert rv.status_code == 400
    body = rv.get_json()
    assert body['success'] is False