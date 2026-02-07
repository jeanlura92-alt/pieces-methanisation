#!/usr/bin/env python3
"""
Test script to verify all legal compliance routes
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_route(path, description):
    """Test a GET route"""
    try:
        response = client.get(path)
        if response.status_code == 200:
            print(f"✅ {description}: {path}")
            return True
        else:
            print(f"❌ {description}: {path} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {description}: {path} (Error: {e})")
        return False

def main():
    print("\n" + "="*70)
    print("TESTING LEGAL COMPLIANCE ROUTES")
    print("="*70 + "\n")
    
    routes = [
        # Core pages
        ("/", "Home page"),
        ("/annonces", "Listings page"),
        ("/contact", "Contact page"),
        
        # Legal pages (LCEN, RGPD, ePrivacy, Code de Commerce)
        ("/mentions-legales", "Legal notices (LCEN)"),
        ("/cgv", "Terms & Conditions (Code de Commerce)"),
        ("/politique-confidentialite", "Privacy Policy (RGPD)"),
        ("/cookies", "Cookie management (ePrivacy)"),
        
        # DSA compliance
        ("/comment-ca-marche", "How it works (DSA transparency)"),
        ("/signaler", "Report form (DSA)"),
        
        # Admin dashboard
        ("/admin/reports", "Admin reports dashboard"),
        
        # Wizard flow
        ("/deposer/step1", "Wizard step 1"),
    ]
    
    passed = 0
    failed = 0
    
    for path, description in routes:
        if test_route(path, description):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    if failed > 0:
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
