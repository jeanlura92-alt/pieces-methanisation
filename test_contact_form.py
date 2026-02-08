"""
Test contact form functionality
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_contact_get():
    """Test GET request to contact page"""
    response = client.get("/contact")
    assert response.status_code == 200
    assert "Contactez-nous" in response.text

def test_contact_post_success():
    """Test POST request to contact form with valid data"""
    response = client.post(
        "/contact",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "test-subject",
            "message": "This is a test message"
        }
    )
    assert response.status_code == 200
    assert "Message envoyé !" in response.text
    assert "Votre message a été envoyé avec succès" in response.text

def test_contact_post_all_fields():
    """Test POST request with all optional fields"""
    response = client.post(
        "/contact",
        data={
            "name": "John Doe",
            "company": "Test Company",
            "email": "john@example.com",
            "phone": "+33123456789",
            "subject": "question-annonce",
            "reference": "#123",
            "message": "Complete test message with all fields"
        }
    )
    assert response.status_code == 200
    assert "Message envoyé !" in response.text

if __name__ == "__main__":
    print("Running contact form tests...")
    test_contact_get()
    print("✓ GET /contact works")
    test_contact_post_success()
    print("✓ POST /contact with required fields works")
    test_contact_post_all_fields()
    print("✓ POST /contact with all fields works")
    print("\n✅ All tests passed!")
