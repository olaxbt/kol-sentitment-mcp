"""
Basic tests for the KOL Sentiment MCP Flask application
"""
import pytest
from app.app import create_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    app = create_app({
        'TESTING': True,
        'MASA_API_KEY': 'test_key',
        'MASA_API_URL': 'http://test.api.url'
    })
    return app

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_mcp_ping(client):
    """Test the MCP ping endpoint"""
    response = client.get('/api/mcp/ping')
    assert response.status_code == 200
    assert response.json['status'] == 'ok' 