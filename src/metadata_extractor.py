import pandas as pd
from lxml import etree
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LegislationMetadataExtractor:
    """
    Extracts metadata from legislation XML documents.
    Based on the official legislation.gov.uk XML schema.
    """
    
    def __init__(self):
        # Define namespace map based on official documentation
        self.namespaces = {
            'leg': 'http://www.legislation.gov.uk/namespaces/legislation',
            'ukm': 'http://www.legislation.gov.uk/namespaces/metadata',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dct': 'http://purl.org/dc/terms/',
            'atom': 'http://www.w3.org/2005/Atom',
            'xhtml': 'http://www.w3.org/1999/xhtml'
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
                'amendments': self._extract_amendments(root),
                'legislation_type': self._extract_legislation_type(root),
                'number': self._extract_number(root)
            }
            
            return metadata
            
        except etree.XMLSyntaxError as e:
            logger.error(f'Failed to parse XML: {str(e)}')
            raise
    
    def _extract_title(self, root: etree._Element) -> str:
        """Extract legislation title from metadata or document structure."""
        # Try metadata first
        title_elem = root.find('.//ukm:Metadata/dc:title', self.namespaces)
        if title_elem is not None and title_elem.text:
            return title_elem.text
        
        # Try alternative locations
        title_elem = root.find('.//leg:Title', self.namespaces)
        if title_elem is not None and title_elem.text:
            return title_elem.text
            
        # Try TitleBlock
        title_elem = root.find('.//leg:TitleBlock/leg:Title', self.namespaces)
        if title_elem is not None and title_elem.text:
            return title_elem.text
        
        return 'Unknown Title'
    
    def _extract_year(self, root: etree._Element) -> Optional[int]:
        """Extract legislation year from metadata."""
        # Try metadata
        year_elem = root.find('.//ukm:Metadata/ukm:Year', self.namespaces)
        if year_elem is not None and year_elem.get('Value'):
            try:
                return int(year_elem.get('Value'))
            except ValueError:
                pass
        
        # Try alternative locations
        year_elem = root.find('.//leg:Year', self.namespaces)
        if year_elem is not None and year_elem.text:
            try:
                return int(year_elem.text)
            except ValueError:
                pass
        
        return None
    
    def _extract_document_uri(self, root: etree._Element) -> str:
        """Extract document URI from metadata."""
        # Try DocumentURI
        uri_elem = root.find('.//ukm:Metadata/ukm:DocumentURI', self.namespaces)
        if uri_elem is not None and uri_elem.get('Value'):
            return uri_elem.get('Value')
        
        # Try atom:link with rel="self"
        link_elem = root.find('.//atom:link[@rel="self"]', self.namespaces)
        if link_elem is not None and link_elem.get('href'):
            return link_elem.get('href')
        
        return ''
    
    def _extract_legislation_type(self, root: etree._Element) -> str:
        """Extract legislation type."""
        # Try DocumentMainType
        type_elem = root.find('.//ukm:Metadata/ukm:DocumentMainType', self.namespaces)
        if type_elem is not None and type_elem.get('Value'):
            return type_elem.get('Value')
        
        return 'Unknown'
    
    def _extract_number(self, root: etree._Element) -> Optional[str]:
        """Extract legislation number."""
        # Try Number
        number_elem = root.find('.//ukm:Metadata/ukm:Number', self.namespaces)
        if number_elem is not None and number_elem.get('Value'):
            return number_elem.get('Value')
        
        return None
    
    def _extract_sections(self, root: etree._Element) -> List[Dict[str, Any]]:
        """Extract section information from the document body."""
        sections = []
        
        # Look for different types of sections/provisions
        section_selectors = [
            './/leg:P1',      # Primary sections
            './/leg:P2',      # Sub-sections
            './/leg:P3',      # Sub-sub-sections
            './/leg:Section', # Generic sections
            './/leg:Part',    # Parts
            './/leg:Chapter'  # Chapters
        ]
        
        for selector in section_selectors:
            for section in root.xpath(selector, namespaces=self.namespaces):
                section_data = {
                    'id': section.get('id', ''),
                    'type': section.tag.split('}')[-1] if '}' in section.tag else section.tag,
                    'number': self._get_section_number(section),
                    'title': self._get_section_title(section),
                    'content': self._get_section_text(section)
                }
                sections.append(section_data)
        
        return sections
    
    def _get_section_number(self, section: etree._Element) -> str:
        """Get section number."""
        # Try Pnumber element
        number_elem = section.find('.//leg:Pnumber', self.namespaces)
        if number_elem is not None and number_elem.text:
            return number_elem.text.strip()
        
        # Try Number element
        number_elem = section.find('.//leg:Number', self.namespaces)
        if number_elem is not None and number_elem.text:
            return number_elem.text.strip()
        
        # Use id attribute if available
        return section.get('id', '')
    
    def _get_section_title(self, section: etree._Element) -> str:
        """Get section title."""
        # Try Title element
        title_elem = section.find('.//leg:Title', self.namespaces)
        if title_elem is not None:
            # Get text content, handling nested elements
            return ' '.join(title_elem.itertext()).strip()
        
        return ''
    
    def _get_section_text(self, section: etree._Element) -> str:
        """Get section text content."""
        # Try Text element
        text_elem = section.find('.//leg:Text', self.namespaces)
        if text_elem is not None:
            # Get all text content, truncated for summary
            text = ' '.join(text_elem.itertext()).strip()
            return text[:500] + '...' if len(text) > 500 else text
        
        return ''
    
    def _extract_amendments(self, root: etree._Element) -> List[Dict[str, Any]]:
        """Extract amendment information from unapplied effects."""
        amendments = []
        
        # Look for unapplied effects in metadata
        for effect in root.xpath('.//ukm:UnappliedEffect', namespaces=self.namespaces):
            amendment_data = {
                'id': effect.get('Id', ''),
                'type': effect.get('Type', ''),
                'affecting_uri': effect.get('AffectingURI', ''),
                'affected_uri': effect.get('AffectedURI', ''),
                'description': effect.get('Notes', '')
            }
            amendments.append(amendment_data)
        
        return amendments
    
    def to_dataframe(self, metadata: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Convert metadata to pandas DataFrames.
        
        Args:
            metadata: Dictionary of metadata
            
        Returns:
            Dictionary containing DataFrames
        """
        # Create base DataFrame with main metadata
        base_data = {
            'title': [metadata['title']],
            'year': [metadata['year']],
            'document_uri': [metadata['document_uri']],
            'legislation_type': [metadata['legislation_type']],
            'number': [metadata['number']]
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