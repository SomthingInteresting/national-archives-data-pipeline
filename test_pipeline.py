#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to verify the National Archives data pipeline modules.
"""

import sys
import os
sys.path.append('src')

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    try:
        from api_client import LegislationAPIClient
        from atom_parser import parse_atom_feed
        from xml_validator import XMLValidator
        from metadata_extractor import LegislationMetadataExtractor
        from reporting import generate_pdf_report
        print("[PASS] All imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_api_client():
    """Test basic API client functionality."""
    print("\nTesting API client...")
    try:
        from api_client import LegislationAPIClient
        client = LegislationAPIClient()
        print("[PASS] API client initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] API client error: {e}")
        return False

def test_xml_validator():
    """Test XML validator initialization."""
    print("\nTesting XML validator...")
    try:
        from xml_validator import XMLValidator
        validator = XMLValidator()
        schema_name = validator.get_schema_for_legislation('ukpga/2020/1')
        print(f"[PASS] XML validator initialized, schema: {schema_name}")
        return True
    except Exception as e:
        print(f"[FAIL] XML validator error: {e}")
        return False

def test_metadata_extractor():
    """Test metadata extractor initialization."""
    print("\nTesting metadata extractor...")
    try:
        from metadata_extractor import LegislationMetadataExtractor
        extractor = LegislationMetadataExtractor()
        print("[PASS] Metadata extractor initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Metadata extractor error: {e}")
        return False

def test_atom_parser():
    """Test atom parser with sample data."""
    print("\nTesting atom parser...")
    try:
        from atom_parser import parse_atom_feed
        
        # Sample minimal Atom feed for testing
        sample_atom = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>http://www.legislation.gov.uk/ukpga/2020/1</id>
        <title>Coronavirus Act 2020</title>
        <updated>2020-03-25T00:00:00Z</updated>
    </entry>
</feed>'''
        
        df = parse_atom_feed(sample_atom)
        print(f"[PASS] Atom parser working, parsed {len(df)} entries")
        return True
    except Exception as e:
        print(f"[FAIL] Atom parser error: {e}")
        return False

def main():
    """Run all tests."""
    print("National Archives Data Pipeline - Module Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_api_client,
        test_xml_validator,
        test_metadata_extractor,
        test_atom_parser
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'=' * 50}")
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! Pipeline modules are working correctly.")
        return True
    else:
        print("[ERROR] Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 