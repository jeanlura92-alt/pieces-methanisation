#!/usr/bin/env python3
"""
Test script to verify V2 simplification changes
"""

import sys
from datetime import datetime, timedelta

def test_config():
    """Test that config has correct MAX_PHOTOS_PER_LISTING"""
    print("Testing config.py...")
    from app import config
    
    assert config.MAX_PHOTOS_PER_LISTING == 1, \
        f"Expected MAX_PHOTOS_PER_LISTING=1, got {config.MAX_PHOTOS_PER_LISTING}"
    print("✓ MAX_PHOTOS_PER_LISTING is set to 1")


def test_db_functions():
    """Test that inquiry functions are removed and expiration functions exist"""
    print("\nTesting db.py...")
    from app import db
    
    # Check that inquiry functions are removed
    assert not hasattr(db, 'create_inquiry'), \
        "create_inquiry should be removed from db.py"
    print("✓ create_inquiry function removed")
    
    assert not hasattr(db, 'get_listing_inquiries'), \
        "get_listing_inquiries should be removed from db.py"
    print("✓ get_listing_inquiries function removed")
    
    assert not hasattr(db, 'count_listing_inquiries'), \
        "count_listing_inquiries should be removed from db.py"
    print("✓ count_listing_inquiries function removed")
    
    # Check that expiration function exists
    assert hasattr(db, 'expire_old_listings'), \
        "expire_old_listings function should exist in db.py"
    print("✓ expire_old_listings function exists")


def test_routes():
    """Test that dashboard and inquiry routes are removed"""
    print("\nTesting main.py routes...")
    from app.main import app
    
    routes = [route.path for route in app.routes]
    
    # Check that dashboard route is removed
    assert "/dashboard" not in routes, \
        "/dashboard route should be removed"
    print("✓ /dashboard route removed")
    
    # Check that inquiry route is removed (POST to listing detail)
    inquiry_route_exists = any(
        "/annonces/{listing_id}/inquiry" in route.path 
        for route in app.routes
    )
    assert not inquiry_route_exists, \
        "/annonces/{listing_id}/inquiry route should be removed"
    print("✓ /annonces/{listing_id}/inquiry route removed")


def test_templates():
    """Test that dashboard template is removed"""
    print("\nTesting templates...")
    import os
    
    template_dir = "app/templates"
    assert os.path.exists(template_dir), \
        f"Template directory {template_dir} should exist"
    
    dashboard_template = os.path.join(template_dir, "dashboard.html")
    assert not os.path.exists(dashboard_template), \
        "dashboard.html template should be removed"
    print("✓ dashboard.html template removed")
    
    # Check that detail.html exists (should be modified, not removed)
    detail_template = os.path.join(template_dir, "detail.html")
    assert os.path.exists(detail_template), \
        "detail.html template should exist"
    
    # Check that detail.html contains contact info display (not inquiry form)
    with open(detail_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'mailto:' in content, \
        "detail.html should contain mailto: link for email"
    print("✓ detail.html contains mailto: link")
    
    assert 'tel:' in content, \
        "detail.html should contain tel: link for phone"
    print("✓ detail.html contains tel: link")
    
    assert 'name="buyer_name"' not in content, \
        "detail.html should not contain inquiry form"
    print("✓ detail.html does not contain inquiry form")
    
    # Check wizard_step3.html
    wizard_step3 = os.path.join(template_dir, "wizard_step3.html")
    assert os.path.exists(wizard_step3), \
        "wizard_step3.html template should exist"
    
    with open(wizard_step3, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'multiple' not in content or 'multiple' not in content.lower(), \
        "wizard_step3.html should not have 'multiple' attribute on file input"
    print("✓ wizard_step3.html file input does not have 'multiple' attribute")
    
    assert 'Sélectionnez 1 photo' in content or 'une photo' in content.lower(), \
        "wizard_step3.html should indicate 1 photo upload"
    print("✓ wizard_step3.html indicates 1 photo limit")


def test_migration_files():
    """Test that migration files exist"""
    print("\nTesting migration files...")
    import os
    
    migration_file = "MIGRATION_V2.sql"
    assert os.path.exists(migration_file), \
        f"{migration_file} should exist"
    print(f"✓ {migration_file} exists")
    
    changelog_file = "CHANGELOG_V2.md"
    assert os.path.exists(changelog_file), \
        f"{changelog_file} should exist"
    print(f"✓ {changelog_file} exists")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing V2 Simplification Changes")
    print("=" * 60)
    
    try:
        test_config()
        test_db_functions()
        test_routes()
        test_templates()
        test_migration_files()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
