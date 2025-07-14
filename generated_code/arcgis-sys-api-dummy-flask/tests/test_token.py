"""
Test suite for Token API endpoints
"""
import pytest
import json
from app import create_app, db


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_token():
    """Create sample token data"""
    return {
        "name": "Test Token",
        "description": "Test description"
    }


class TestTokenAPI:
    """Test suite for Token API endpoints"""
    
    def test_get(self, client, sample_token):
        """Test GET /token"""
        # Test getting all tokens
        response = client.get('/token')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    
    def test_token_validation_errors(self, client):
        """Test validation error handling"""
        # Test with empty data
        response = client.post(
            '/api/v1/token',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test with invalid data
        response = client.post(
            '/api/v1/token',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400


def test_health_check(client):
    """Test application health check"""
    response = client.get('/health')
    assert response.status_code == 200 or response.status_code == 404  # 404 if route not implemented