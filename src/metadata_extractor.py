import pandas as pd
from lxml import etree
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MetadataExtractor:
    """Extract metadata from UK legislation XML documents."""
    
    def __init__(self):
        # Updated namespaces based on actual XML structure
        self.namespaces = {
            'leg': 'http://www.legislation.gov.uk/namespaces/legislation',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
    
    def extract_metadata(self, xml_content: str) -> Dict[str, Any]:
        """
        Extract metadata from XML content.
        
        Args:
            xml_content: Raw XML content as string
            
        Returns:
            Dictionary containing extracted metadata
        """
        try:
            # Parse XML
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Extract basic metadata
            metadata = {
                'document_uri': root.get('DocumentURI', ''),
                'id_uri': root.get('IdURI', ''),
                'number_of_provisions': root.get('NumberOfProvisions', ''),
                'schema_version': root.get('SchemaVersion', ''),
                'restrict_extent': root.get('RestrictExtent', ''),
                'restrict_start_date': root.get('RestrictStartDate', ''),
                'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract title - try multiple sources
            title = self._extract_title(root)
            metadata['title'] = title
            
            # Extract long title
            long_title = self._extract_long_title(root)
            metadata['long_title'] = long_title
            
            # Extract year from document URI or ID URI
            year = self._extract_year(metadata.get('document_uri', ''))
            metadata['year'] = year
            
            # Extract legislation type and number
            leg_type, leg_number = self._extract_type_and_number(metadata.get('document_uri', ''))
            metadata['legislation_type'] = leg_type
            metadata['legislation_number'] = leg_number
            
            # Count sections and schedules
            sections = self._count_sections(root)
            schedules = self._count_schedules(root)
            metadata['sections_count'] = sections
            metadata['schedules_count'] = schedules
            
            # Extract key sections
            key_sections = self._extract_key_sections(root)
            metadata['key_sections'] = key_sections
            
            logger.info(f"Successfully extracted metadata for: {title}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {
                'error': str(e),
                'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _extract_title(self, root) -> str:
        """Extract the main title from various possible locations."""
        # Try Dublin Core title first
        dc_title = root.find('.//dc:title', self.namespaces)
        if dc_title is not None and dc_title.text:
            return dc_title.text.strip()
        
        # Try legislation title
        leg_title = root.find('.//leg:Title', self.namespaces)
        if leg_title is not None and leg_title.text:
            return leg_title.text.strip()
        
        # Try any title element in legislation namespace
        any_title = root.find('.//{http://www.legislation.gov.uk/namespaces/legislation}Title')
        if any_title is not None and any_title.text:
            return any_title.text.strip()
        
        return 'Unknown Title'
    
    def _extract_long_title(self, root) -> str:
        """Extract the long title."""
        long_title = root.find('.//leg:LongTitle', self.namespaces)
        if long_title is not None and long_title.text:
            return long_title.text.strip()
        
        # Try without namespace prefix
        long_title = root.find('.//{http://www.legislation.gov.uk/namespaces/legislation}LongTitle')
        if long_title is not None and long_title.text:
            return long_title.text.strip()
        
        return ''
    
    def _extract_year(self, uri: str) -> str:
        """Extract year from URI."""
        if not uri:
            return ''
        
        # Extract year from pattern like '/ukpga/2020/7'
        parts = uri.split('/')
        for part in parts:
            if part.isdigit() and len(part) == 4 and part.startswith('20'):
                return part
        
        return ''
    
    def _extract_type_and_number(self, uri: str) -> tuple:
        """Extract legislation type and number from URI."""
        if not uri:
            return '', ''
        
        try:
            # Pattern: .../ukpga/2020/7
            parts = uri.split('/')
            if len(parts) >= 3:
                leg_type = parts[-3]  # ukpga
                leg_number = parts[-1]  # 7
                return leg_type, leg_number
        except:
            pass
        
        return '', ''
    
    def _count_sections(self, root) -> int:
        """Count the number of sections."""
        sections = root.findall('.//leg:P1', self.namespaces)
        if not sections:
            # Try without namespace prefix
            sections = root.findall('.//{http://www.legislation.gov.uk/namespaces/legislation}P1')
        
        return len(sections)
    
    def _count_schedules(self, root) -> int:
        """Count the number of schedules."""
        schedules = root.findall('.//leg:Schedule', self.namespaces)
        if not schedules:
            # Try without namespace prefix
            schedules = root.findall('.//{http://www.legislation.gov.uk/namespaces/legislation}Schedule')
        
        return len(schedules)
    
    def _extract_key_sections(self, root) -> list:
        """Extract key section titles and numbers."""
        sections = []
        
        # Find all P1 elements (main sections)
        p1_elements = root.findall('.//leg:P1', self.namespaces)
        if not p1_elements:
            p1_elements = root.findall('.//{http://www.legislation.gov.uk/namespaces/legislation}P1')
        
        logger.debug(f"Found {len(p1_elements)} P1 elements")
        
        for i, p1 in enumerate(p1_elements[:10]):  # Limit to first 10 sections
            # Get section number
            pnum = p1.find('.//leg:Pnumber', self.namespaces)
            if pnum is None:
                pnum = p1.find('.//{http://www.legislation.gov.uk/namespaces/legislation}Pnumber')
            
            section_num = pnum.text.strip() if pnum is not None and pnum.text else ''
            
            # Extract section title from Text elements
            section_title = ''
            
            # Look in P1para for Text elements
            p1para = p1.find('.//leg:P1para', self.namespaces)
            if p1para is None:
                p1para = p1.find('.//{http://www.legislation.gov.uk/namespaces/legislation}P1para')
            
            if p1para is not None:
                # Find Text elements within P1para
                text_elem = p1para.find('.//leg:Text', self.namespaces)
                if text_elem is None:
                    text_elem = p1para.find('.//{http://www.legislation.gov.uk/namespaces/legislation}Text')
                
                if text_elem is not None and text_elem.text:
                    # Extract first sentence or meaningful phrase as title
                    full_text = text_elem.text.strip()
                    
                    # Skip placeholder sections (dots or very short content)
                    if len(full_text) > 10 and not full_text.startswith('. . .'):
                        # Take first sentence or first 80 characters as title
                        if '. ' in full_text:
                            section_title = full_text.split('. ')[0] + '.'
                        elif '—' in full_text:  # Common in legislation
                            section_title = full_text.split('—')[0].strip()
                        else:
                            section_title = full_text[:80] + '...' if len(full_text) > 80 else full_text
                
                # If no Text element, try to construct title from structure
                if not section_title:
                    # Check if this section has subsections (P2, P3, etc.)
                    subsections = []
                    for child in p1para:
                        child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        if child_tag.startswith('P') and child_tag[1:].isdigit():
                            subsections.append(child_tag)
                    
                    if subsections:
                        section_title = f"Section with {len(subsections)} subsections ({', '.join(subsections)})"
            
            # Fallback: try to find any meaningful text in the P1 section
            if not section_title:
                # Look for any text content in the entire P1 section
                all_text = []
                for elem in p1.iter():
                    if elem.text and elem.text.strip() and len(elem.text.strip()) > 5:
                        text = elem.text.strip()
                        if not text.startswith('. . .') and text != section_num:
                            all_text.append(text)
                
                if all_text:
                    section_title = all_text[0][:80] + '...' if len(all_text[0]) > 80 else all_text[0]
            
            # Debug logging for first few sections
            if i < 5:
                logger.debug(f"Section {i}: number='{section_num}', title='{section_title}'")
            
            # Only add sections that have a number or meaningful title
            if section_num and (section_title and not section_title.startswith('Section with')):
                sections.append({
                    'number': section_num,
                    'title': section_title
                })
            elif section_num and not section_title:
                # Add with a generic title if we have a number but no content
                sections.append({
                    'number': section_num,
                    'title': f"Section {section_num}"
                })
        
        logger.debug(f"Extracted {len(sections)} sections with titles")
        return sections

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
            'number': [metadata['legislation_number']]
        }
        df = pd.DataFrame(base_data)
        
        # Add sections and amendments as separate DataFrames
        sections_df = pd.DataFrame(metadata['key_sections'])
        
        return {
            'main': df,
            'sections': sections_df
        } 