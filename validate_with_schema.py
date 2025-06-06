#!/usr/bin/env python3
"""
CLML Schema Validation Script

Demonstrates enhanced XML validation using official Crown Legislation Markup Language schemas.
This script shows the educational value of using proper standards-based validation.
"""

import sys
from pathlib import Path
from src.api_client import LegislationAPIClient
from src.xml_validator import XMLValidator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_coronavirus_act():
    """
    Validate the Coronavirus Act 2020 against CLML schema.
    This demonstrates proper schema-based validation vs. blind parsing.
    """
    print('🔍 CLML Schema Validation Demo')
    print('=' * 50)
    
    # Initialize components
    client = LegislationAPIClient()
    validator = XMLValidator()
    
    try:
        # Fetch legislation XML
        print('📥 Fetching Coronavirus Act 2020 XML...')
        xml_content = client.get_legislation_xml('ukpga', '2020', '7')
        
        # Perform comprehensive CLML validation
        print('\n🔬 Performing CLML Schema Validation...')
        validation_results = validator.validate_against_clml(xml_content, check_metadata=True)
        
        # Display results
        print(f'\n📊 Validation Results:')
        print(f'   ✅ Valid: {validation_results["is_valid"]}')
        
        if validation_results['namespaces']:
            print(f'\n🏷️  XML Namespaces Found:')
            for prefix, uri in validation_results['namespaces'].items():
                if prefix:  # Skip default namespace
                    print(f'   {prefix}: {uri}')
        
        if validation_results['errors']:
            print(f'\n❌ Schema Errors ({len(validation_results["errors"])}):')
            for error in validation_results['errors'][:5]:  # Show first 5
                print(f'   • {error}')
            if len(validation_results['errors']) > 5:
                print(f'   ... and {len(validation_results["errors"]) - 5} more')
        
        if validation_results['warnings']:
            print(f'\n⚠️  Schema Warnings ({len(validation_results["warnings"])}):')
            for warning in validation_results['warnings'][:5]:  # Show first 5
                print(f'   • {warning}')
            if len(validation_results['warnings']) > 5:
                print(f'   ... and {len(validation_results["warnings"]) - 5} more')
        
        # Educational insights
        print(f'\n🎓 Educational Insights:')
        print(f'   • Using official CLML schema vs. blind parsing')
        print(f'   • Proper namespace validation ensures standards compliance')
        print(f'   • Schema-driven development prevents parsing errors')
        print(f'   • Government data follows established markup standards')
        
        # Compare to our earlier approach
        print(f'\n🔄 Before vs. After Schema Integration:')
        print(f'   Before: Trial-and-error XML parsing with namespace guessing')
        print(f'   After:  Standards-based validation with official schemas')
        print(f'   Result: More robust, professional, and educational approach')
        
        return validation_results['is_valid']
        
    except Exception as e:
        logger.error(f'Validation failed: {str(e)}')
        return False

def check_schema_files():
    """
    Check if schema files are properly downloaded and accessible.
    """
    print('\n📁 Checking Schema Files...')
    schema_dir = Path('data/raw/schemas')
    
    expected_files = [
        'legislation.xsd',
        'schemaLegislationCore.xsd', 
        'schemaLegislationMetadata.xsd',
        'README.md'
    ]
    
    all_present = True
    for file_name in expected_files:
        file_path = schema_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f'   ✅ {file_name} ({size:,} bytes)')
        else:
            print(f'   ❌ {file_name} (missing)')
            all_present = False
    
    return all_present

def main():
    """
    Main demonstration function.
    """
    print('🏛️  National Archives Data Pipeline - CLML Schema Integration Demo')
    print('=' * 70)
    
    # Check schema files
    if not check_schema_files():
        print('\n❌ Some schema files are missing. Please ensure schemas are downloaded.')
        return 1
    
    # Run validation demo
    success = validate_coronavirus_act()
    
    if success:
        print(f'\n🎉 Schema validation successful!')
        print(f'   The pipeline now uses official CLML standards for robust XML processing.')
    else:
        print(f'\n⚠️  Schema validation encountered issues.')
        print(f'   This demonstrates the value of proper validation in data pipelines.')
    
    print(f'\n📚 Learning Outcomes:')
    print(f'   • Standards-based XML validation using government schemas')
    print(f'   • Professional development practices with official documentation')
    print(f'   • Understanding UK legislation markup language (CLML)')
    print(f'   • Schema-driven development vs. reverse engineering')
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 