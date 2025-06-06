import requests
import xmlschema
from lxml import etree
from typing import List, Dict, Any, Optional
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class XMLValidator:
    """
    Validates XML against CLML (Crown Legislation Markup Language) schemas.
    Uses official UK government schemas for proper validation.
    """
    
    SCHEMA_BASE_URL = 'https://www.legislation.gov.uk/schema'
    SCHEMA_CACHE_DIR = Path('data/raw/schemas')
    
    def __init__(self):
        self.schema_cache = {}
        self.SCHEMA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Define core CLML schemas we use
        self.core_schemas = {
            'legislation': 'legislation.xsd',
            'core': 'schemaLegislationCore.xsd', 
            'metadata': 'schemaLegislationMetadata.xsd'
        }
    
    def _download_schema(self, schema_name: str) -> str:
        """
        Download schema from legislation.gov.uk or use cached version.
        
        Args:
            schema_name: Name of the schema file
            
        Returns:
            Path to local schema file
        """
        schema_path = self.SCHEMA_CACHE_DIR / schema_name
        
        if not schema_path.exists():
            url = f'{self.SCHEMA_BASE_URL}/{schema_name}'
            try:
                response = requests.get(url)
                response.raise_for_status()
                schema_path.write_text(response.text)
            except requests.RequestException as e:
                logger.error(f'Failed to download schema {schema_name}: {str(e)}')
                raise
        
        return str(schema_path)
    
    def validate_xml(self, xml_content: str, schema_name: str) -> List[str]:
        """
        Validate XML against specified schema.
        
        Args:
            xml_content: XML content to validate
            schema_name: Name of the schema file to validate against
            
        Returns:
            List of validation errors (empty if valid)
            
        Raises:
            xmlschema.XMLSchemaException: If schema is invalid
            etree.XMLSyntaxError: If XML is malformed
        """
        try:
            # Get schema
            if schema_name not in self.schema_cache:
                schema_path = self._download_schema(schema_name)
                self.schema_cache[schema_name] = xmlschema.XMLSchema(schema_path)
            
            schema = self.schema_cache[schema_name]
            
            # Parse XML
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Validate
            errors = []
            for error in schema.iter_errors(root):
                errors.append(str(error))
            
            return errors
            
        except (xmlschema.XMLSchemaException, etree.XMLSyntaxError) as e:
            logger.error(f'Validation failed: {str(e)}')
            raise
    
    def validate_legislation_xml(self, xml_content: str) -> List[str]:
        """
        Validate legislation XML against CLML schema.
        
        Args:
            xml_content: XML content to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        return self.validate_xml(xml_content, self.core_schemas['legislation'])
    
    def validate_against_clml(self, xml_content: str, check_metadata: bool = True) -> Dict[str, Any]:
        """
        Comprehensive CLML validation with detailed results.
        
        Args:
            xml_content: XML content to validate
            check_metadata: Whether to also validate metadata structure
            
        Returns:
            Dict with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'schema_version': None,
            'namespaces': {}
        }
        
        try:
            # Parse XML to check structure
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Extract namespaces
            results['namespaces'] = root.nsmap
            
            # Check for expected CLML namespaces
            expected_namespaces = {
                'leg': 'http://www.legislation.gov.uk/namespaces/legislation',
                'ukm': 'http://www.legislation.gov.uk/namespaces/metadata'
            }
            
            for prefix, uri in expected_namespaces.items():
                if uri not in root.nsmap.values():
                    results['warnings'].append(f'Expected namespace {prefix}:{uri} not found')
            
            # Validate against main legislation schema
            schema_errors = self.validate_legislation_xml(xml_content)
            if schema_errors:
                results['is_valid'] = False
                results['errors'].extend(schema_errors)
            
            # Additional metadata validation if requested
            if check_metadata and results['is_valid']:
                metadata_errors = self._validate_metadata_structure(root)
                results['warnings'].extend(metadata_errors)
                
        except Exception as e:
            results['is_valid'] = False
            results['errors'].append(f'Validation failed: {str(e)}')
        
        return results
    
    def _validate_metadata_structure(self, root) -> List[str]:
        """
        Validate metadata structure against CLML expectations.
        
        Args:
            root: Parsed XML root element
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check for common metadata elements
        metadata_elements = [
            'DocumentMainType',
            'DocumentStatus', 
            'DocumentCategory',
            'Year',
            'Number'
        ]
        
        ukm_ns = '{http://www.legislation.gov.uk/namespaces/metadata}'
        
        for element_name in metadata_elements:
            if root.find(f'.//{ukm_ns}{element_name}') is None:
                warnings.append(f'Metadata element {element_name} not found')
        
        return warnings
    
    def get_schema_for_legislation(self, legislation_id: str) -> str:
        """
        Determine appropriate schema for legislation type.
        
        Args:
            legislation_id: ID of the legislation (e.g., 'ukpga/2020/1')
            
        Returns:
            Name of appropriate schema file
        """
        # For CLML, we use the main legislation schema for all types
        return self.core_schemas['legislation'] 