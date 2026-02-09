#!/usr/bin/env python3
"""
Test script to verify SMTP configuration
Run with: python test_smtp_config.py
"""
import asyncio
import sys
from app import config
from app.email import send_contact_email

async def test_smtp():
    print("=" * 60)
    print("Testing SMTP Configuration")
    print("=" * 60)
    print()
    
    # Check configuration
    print("SMTP Configuration:")
    print(f"  SMTP_HOST: {config.SMTP_HOST or '❌ Not configured'}")
    print(f"  SMTP_PORT: {config.SMTP_PORT}")
    print(f"  SMTP_USER: {config.SMTP_USER or '❌ Not configured'}")
    print(f"  SMTP_PASSWORD: {'✅ Set' if config.SMTP_PASSWORD else '❌ Not set'}")
    print(f"  CONTACT_EMAIL: {config.CONTACT_EMAIL}")
    print()
    
    if not config.SMTP_HOST:
        print("⚠️  SMTP not configured - emails will not be sent")
        print("   Configure SMTP in .env file to enable email sending")
        return False
    
    print("Sending test email...")
    print()
    
    # Send test email
    success = await send_contact_email(
        name="Test User",
        email="test@example.com",
        phone="+33123456789",
        company="Test Company",
        subject="test-email",
        reference=None,
        message="This is a test email from the SMTP configuration test script."
    )
    
    if success:
        print("✅ Test email sent successfully!")
        print(f"   Check inbox: {config.CONTACT_EMAIL}")
        return True
    else:
        print("❌ Failed to send test email")
        print("   Check logs above for error details")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_smtp())
    sys.exit(0 if result else 1)
