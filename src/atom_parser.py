import pandas as pd
from lxml import etree
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def parse_atom_feed(xml_content: str) -> pd.DataFrame:
    """
    Parse an Atom feed XML and extract legislation information.
    
    Args:
        xml_content: Raw Atom feed XML as string
        
    Returns:
        DataFrame with columns: [uri, title, date]
        
    Raises:
        etree.XMLSyntaxError: If the XML is malformed
    """
    try:
        # Parse XML
        root = etree.fromstring(xml_content.encode('utf-8'))
        
        # Define namespace map
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'leg': 'http://www.legislation.gov.uk/namespaces/legislation'
        }
        
        # Extract entries
        entries = []
        for entry in root.xpath('//atom:entry', namespaces=namespaces):
            try:
                uri = entry.find('atom:id', namespaces).text
                title = entry.find('atom:title', namespaces).text
                date = entry.find('atom:updated', namespaces).text
                
                entries.append({
                    'uri': uri,
                    'title': title,
                    'date': date
                })
            except AttributeError as e:
                logger.warning(f'Failed to parse entry: {str(e)}')
                continue
        
        # Create DataFrame
        df = pd.DataFrame(entries)
        
        # Convert date column to datetime
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            
        return df
        
    except etree.XMLSyntaxError as e:
        logger.error(f'Failed to parse XML: {str(e)}')
        raise 