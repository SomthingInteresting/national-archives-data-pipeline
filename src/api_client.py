import time
import requests
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegislationAPIClient:
    """
    Client for interacting with the legislation.gov.uk API.
    Implements rate limiting and error handling.
    """
    
    BASE_URL = 'https://www.legislation.gov.uk'
    RATE_LIMIT_DELAY = 1  # seconds between requests
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('LEGISLATION_API_KEY')
        self.last_request_time = 0
        self.session = requests.Session()
        
    def _rate_limit(self):
        """Implement rate limiting of 1 request per second."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - time_since_last_request)
            
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a rate-limited request to the API.
        
        Args:
            endpoint: API endpoint to call
            params: Optional query parameters
            
        Returns:
            Response object
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        self._rate_limit()
        
        url = f'{self.BASE_URL}/{endpoint}'
        headers = {'Accept': 'application/xml'}
        
        if self.api_key:
            headers['X-API-Key'] = self.api_key
            
        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f'API request failed: {str(e)}')
            raise
    
    def get_atom_feed(self, query: Optional[str] = None) -> str:
        """
        Fetch Atom feed from legislation.gov.uk.
        
        Args:
            query: Optional search query
            
        Returns:
            Raw Atom feed XML as string
        """
        endpoint = 'data.feed'
        params = {'title': query} if query else None
        
        response = self._make_request(endpoint, params)
        return response.text
    
    def get_legislation_xml(self, legislation_id: str) -> str:
        """
        Download XML for a specific piece of legislation.
        
        Args:
            legislation_id: ID of the legislation (e.g., 'ukpga/2020/1')
            
        Returns:
            Raw XML as string
        """
        endpoint = f'{legislation_id}/data.xml'
        response = self._make_request(endpoint)
        return response.text
    
    def get_legislation_metadata(self, legislation_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific piece of legislation.
        
        Args:
            legislation_id: ID of the legislation
            
        Returns:
            Dictionary containing metadata
        """
        xml_content = self.get_legislation_xml(legislation_id)
        # Basic metadata extraction - can be expanded based on needs
        return {
            'id': legislation_id,
            'retrieved_at': datetime.now().isoformat(),
            'content_length': len(xml_content)
        } 