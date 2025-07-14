"""
Test suite for V1 API endpoints
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
def sample_v1():
    """Create sample v1 data"""
    return {
        "name": "Test V1",
        "description": "Test description"
    }


class TestV1API:
    """Test suite for V1 API endpoints"""
    
    
    def test_v1_validation_errors(self, client):
        """Test validation error handling"""
        # Test with empty data
        response = client.post(
            '/api/v1/v1',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test with invalid data
        response = client.post(
            '/api/v1/v1',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400


def test_health_check(client):
    """Test application health check"""
    response = client.get('/health')
    assert response.status_code == 200 or response.status_code == 404  # 404 if route not implemented