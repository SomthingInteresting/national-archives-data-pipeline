import pandas as pd
from lxml import etree
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LegislationMetadataExtractor:
    """
    Extracts metadata from legislation XML documents.
    """
    
    def __init__(self):
        # Define namespace map
        self.namespaces = {
            'leg': 'http://www.legislation.gov.uk/namespaces/legislation',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dct': 'http://purl.org/dc/terms/',
            'atom': 'http://www.w3.org/2005/Atom'
        }
    
    def extract_metadata(self, xml_content: str) -> Dict[str, Any]:
        """
        Extract metadata from legislation XML.
        
        Args:
            xml_content: Raw XML content
            
        Returns:
            Dictionary containing extracted metadata
            
        Raises:
            etree.XMLSyntaxError: If XML is malformed
        """
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            metadata = {
                'title': self._extract_title(root),
                'year': self._extract_year(root),
                'document_uri': self._extract_document_uri(root),
                'sections': self._extract_sections(root),
                'amendments': self._extract_amendments(root)
            }
            
            return metadata
            
        except etree.XMLSyntaxError as e:
            logger.error(f'Failed to parse XML: {str(e)}')
            raise
    
    def _extract_title(self, root: etree._Element) -> str:
        """Extract legislation title."""
        title_elem = root.find('.//leg:Title', self.namespaces)
        return title_elem.text if title_elem is not None else ''
    
    def _extract_year(self, root: etree._Element) -> Optional[int]:
        """Extract legislation year."""
        year_elem = root.find('.//leg:Year', self.namespaces)
        return int(year_elem.text) if year_elem is not None else None
    
    def _extract_document_uri(self, root: etree._Element) -> str:
        """Extract document URI."""
        uri_elem = root.find('.//atom:id', self.namespaces)
        return uri_elem.text if uri_elem is not None else ''
    
    def _extract_sections(self, root: etree._Element) -> List[Dict[str, Any]]:
        """Extract section information."""
        sections = []
        for section in root.xpath('.//leg:Section', self.namespaces):
            section_data = {
                'id': section.get('id', ''),
                'title': section.findtext('.//leg:Title', '', self.namespaces),
                'content': section.findtext('.//leg:Content', '', self.namespaces)
            }
            sections.append(section_data)
        return sections
    
    def _extract_amendments(self, root: etree._Element) -> List[Dict[str, Any]]:
        """Extract amendment information."""
        amendments = []
        for amendment in root.xpath('.//leg:Amendment', self.namespaces):
            amendment_data = {
                'id': amendment.get('id', ''),
                'type': amendment.get('type', ''),
                'date': amendment.findtext('.//leg:Date', '', self.namespaces),
                'description': amendment.findtext('.//leg:Description', '', self.namespaces)
            }
            amendments.append(amendment_data)
        return amendments
    
    def to_dataframe(self, metadata: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert metadata to pandas DataFrame.
        
        Args:
            metadata: Dictionary of metadata
            
        Returns:
            DataFrame containing metadata
        """
        # Create base DataFrame with main metadata
        base_data = {
            'title': [metadata['title']],
            'year': [metadata['year']],
            'document_uri': [metadata['document_uri']]
        }
        df = pd.DataFrame(base_data)
        
        # Add sections and amendments as separate DataFrames
        sections_df = pd.DataFrame(metadata['sections'])
        amendments_df = pd.DataFrame(metadata['amendments'])
        
        return {
            'main': df,
            'sections': sections_df,
            'amendments': amendments_df
        } 