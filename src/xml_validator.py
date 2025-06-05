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
    Validates XML against legislation.gov.uk schemas.
    """
    
    SCHEMA_BASE_URL = 'https://www.legislation.gov.uk/schemas'
    SCHEMA_CACHE_DIR = Path('data/raw/schemas')
    
    def __init__(self):
        self.schema_cache = {}
        self.SCHEMA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
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
    
    def get_schema_for_legislation(self, legislation_id: str) -> str:
        """
        Determine appropriate schema for legislation type.
        
        Args:
            legislation_id: ID of the legislation (e.g., 'ukpga/2020/1')
            
        Returns:
            Name of appropriate schema file
        """
        # Extract legislation type from ID
        legislation_type = legislation_id.split('/')[0]
        
        # Map legislation types to schemas
        schema_map = {
            'ukpga': 'ukpga.xsd',
            'uksi': 'uksi.xsd',
            'nisi': 'nisi.xsd',
            'nia': 'nia.xsd',
            'asp': 'asp.xsd',
            'anaw': 'anaw.xsd',
            'mwa': 'mwa.xsd',
            'ukcm': 'ukcm.xsd'
        }
        
        return schema_map.get(legislation_type, 'legislation.xsd') 