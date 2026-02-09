"""
Test email sending functionality with detailed validation
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import smtplib
from app.main import app
from app import email as email_module

client = TestClient(app)


class TestEmailSending(unittest.TestCase):
    """Test email sending with mocking to verify email content and error handling"""
    
    @patch('app.email.smtplib.SMTP')
    @patch('app.email.config')
    def test_email_content_and_headers(self, mock_config, mock_smtp_class):
        """Test that email is properly formatted with correct headers and body"""
        # Configure mock
        mock_config.SMTP_HOST = 'smtp.example.com'
        mock_config.SMTP_PORT = 587
        mock_config.SMTP_USER = 'test@example.com'
        mock_config.SMTP_PASSWORD = 'password'
        mock_config.CONTACT_EMAIL = 'contact@example.com'
        
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_smtp)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)
        
        # Send email
        import asyncio
        result = asyncio.run(email_module.send_contact_email(
            name="Test User",
            email="user@example.com",
            phone="+33123456789",
            company="Test Company",
            subject="Test Subject",
            reference="#REF123",
            message="This is a test message"
        ))
        
        # Verify result
        self.assertTrue(result, "Email should be sent successfully")
        
        # Verify SMTP connection was attempted
        mock_smtp_class.assert_called_once_with('smtp.example.com', 587)
        
        # Verify SMTP methods were called
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with('test@example.com', 'password')
        
        # Verify send_message was called
        self.assertEqual(mock_smtp.send_message.call_count, 1)
        
        # Get the message that was sent
        sent_message = mock_smtp.send_message.call_args[0][0]
        
        # Verify headers
        self.assertEqual(sent_message['From'], 'test@example.com')
        self.assertEqual(sent_message['To'], 'contact@example.com')
        self.assertIn('Test Subject', sent_message['Subject'])
        
        # Verify body contains all information
        # Email body may be base64 encoded, so decode it
        import base64
        body_part = sent_message.get_payload()[0]
        body = body_part.get_payload()
        
        # Decode if base64 encoded
        if body_part.get('Content-Transfer-Encoding') == 'base64' or '\n' in body:
            try:
                body = base64.b64decode(body).decode('utf-8')
            except:
                pass  # Already decoded
        
        self.assertIn('Test User', body)
        self.assertIn('user@example.com', body)
        self.assertIn('+33123456789', body)
        self.assertIn('Test Company', body)
        self.assertIn('#REF123', body)
        self.assertIn('This is a test message', body)
    
    @patch('app.email.smtplib.SMTP')
    @patch('app.email.config')
    def test_smtp_authentication_error(self, mock_config, mock_smtp_class):
        """Test handling of SMTP authentication errors"""
        # Configure mock
        mock_config.SMTP_HOST = 'smtp.example.com'
        mock_config.SMTP_PORT = 587
        mock_config.SMTP_USER = 'test@example.com'
        mock_config.SMTP_PASSWORD = 'wrong_password'
        mock_config.CONTACT_EMAIL = 'contact@example.com'
        
        mock_smtp = MagicMock()
        mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Authentication failed')
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_smtp)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)
        
        # Send email
        import asyncio
        result = asyncio.run(email_module.send_contact_email(
            name="Test User",
            email="user@example.com",
            phone=None,
            company=None,
            subject="Test Subject",
            reference=None,
            message="Test message"
        ))
        
        # Verify result - should fail gracefully
        self.assertFalse(result, "Email should fail due to authentication error")
    
    @patch('app.email.smtplib.SMTP')
    @patch('app.email.config')
    def test_smtp_connection_error(self, mock_config, mock_smtp_class):
        """Test handling of SMTP connection errors"""
        # Configure mock
        mock_config.SMTP_HOST = 'smtp.example.com'
        mock_config.SMTP_PORT = 587
        mock_config.SMTP_USER = 'test@example.com'
        mock_config.SMTP_PASSWORD = 'password'
        mock_config.CONTACT_EMAIL = 'contact@example.com'
        
        # Simulate connection error
        mock_smtp_class.side_effect = smtplib.SMTPConnectError(421, b'Connection refused')
        
        # Send email
        import asyncio
        result = asyncio.run(email_module.send_contact_email(
            name="Test User",
            email="user@example.com",
            phone=None,
            company=None,
            subject="Test Subject",
            reference=None,
            message="Test message"
        ))
        
        # Verify result - should fail gracefully
        self.assertFalse(result, "Email should fail due to connection error")
    
    @patch('app.email.config')
    def test_mock_mode_when_smtp_not_configured(self, mock_config):
        """Test that email sending works in mock mode when SMTP is not configured"""
        # Configure mock - no SMTP settings
        mock_config.SMTP_HOST = None
        
        # Send email
        import asyncio
        result = asyncio.run(email_module.send_contact_email(
            name="Test User",
            email="user@example.com",
            phone=None,
            company=None,
            subject="Test Subject",
            reference=None,
            message="Test message"
        ))
        
        # Verify result - should succeed in mock mode
        self.assertTrue(result, "Email should succeed in mock mode")
    
    @patch('app.email.smtplib.SMTP')
    @patch('app.email.config')
    def test_email_without_optional_fields(self, mock_config, mock_smtp_class):
        """Test that email works correctly when optional fields are None"""
        # Configure mock
        mock_config.SMTP_HOST = 'smtp.example.com'
        mock_config.SMTP_PORT = 587
        mock_config.SMTP_USER = 'test@example.com'
        mock_config.SMTP_PASSWORD = 'password'
        mock_config.CONTACT_EMAIL = 'contact@example.com'
        
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_smtp)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)
        
        # Send email without optional fields
        import asyncio
        result = asyncio.run(email_module.send_contact_email(
            name="Test User",
            email="user@example.com",
            phone=None,  # Optional
            company=None,  # Optional
            subject="Test Subject",
            reference=None,  # Optional
            message="Test message"
        ))
        
        # Verify result
        self.assertTrue(result, "Email should be sent successfully without optional fields")
        
        # Get the message that was sent
        sent_message = mock_smtp.send_message.call_args[0][0]
        
        # Decode body
        import base64
        body_part = sent_message.get_payload()[0]
        body = body_part.get_payload()
        
        # Decode if base64 encoded
        if body_part.get('Content-Transfer-Encoding') == 'base64' or '\n' in body:
            try:
                body = base64.b64decode(body).decode('utf-8')
            except:
                pass  # Already decoded
        
        # Verify body shows "Non fourni" for missing fields
        self.assertIn('Non fourni', body)
        self.assertIn('Non fournie', body)
        self.assertIn('Aucune', body)


def test_contact_form_integration():
    """Integration test for contact form submission"""
    response = client.post(
        "/contact",
        data={
            "name": "Integration Test",
            "email": "integration@example.com",
            "subject": "integration-test",
            "message": "This is an integration test message"
        }
    )
    
    # Should return success even in mock mode
    assert response.status_code == 200
    assert "Message envoyé !" in response.text or "success" in response.text.lower()


if __name__ == "__main__":
    print("Running email sending tests...")
    unittest.main(verbosity=2)
