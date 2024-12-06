import os
import requests
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more information
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KrakenFlexAPI:
    BASE_URL = "https://api.krakenflex.systems/interview-tests-mock-api/v1"
    
    def __init__(self, api_key: str):
        """Initialize API client with authentication"""
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, max_retries: int = 3, **kwargs) -> Optional[Dict]:
        """
        Generic request method with robust error handling and logging
        
        Args:
            method (str): HTTP method ('get', 'post')
            endpoint (str): API endpoint
            max_retries (int): Number of retry attempts
        
        Returns:
            Optional response data or None
        """
        for attempt in range(max_retries):
            try:
                full_url = f"{self.BASE_URL}/{endpoint}"
                logger.debug(f"Attempt {attempt + 1}: {method.upper()} {full_url}")
                
                response = getattr(requests, method)(
                    full_url, 
                    headers=self.headers, 
                    **kwargs
                )
                
                # Log full response details for debugging
                logger.debug(f"Response Status: {response.status_code}")
                logger.debug(f"Response Headers: {response.headers}")
                
                # Raise for HTTP errors
                response.raise_for_status()
                
                return response.json() if response.content else None
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request Error (Attempt {attempt + 1}): {e}")
                
                # Log response content for 500 errors
                if hasattr(e, 'response'):
                    logger.error(f"Error Response Content: {e.response.text}")
                
                # Final attempt
                if attempt == max_retries - 1:
                    logger.critical("All request attempts failed")
                    raise
    
    def get_outages(self) -> List[Dict]:
        """Retrieve system outages"""
        return self._make_request('get', 'outages') or []
    
    def get_site_info(self, site_id: str) -> Dict:
        """Retrieve site information"""
        return self._make_request('get', f'site-info/{site_id}') or {}
    
    def post_site_outages(self, site_id: str, outages: List[Dict]):
        """Post processed outages for a site"""
        return self._make_request('post', f'site-outages/{site_id}', json=outages)

def process_outages(api: KrakenFlexAPI, site_id: str) -> List[Dict]:
    """Process and filter outages"""
    try:
        # Get all outages
        all_outages = api.get_outages()
        logger.info(f"Total outages retrieved: {len(all_outages)}")
        
        # Get site info
        site_info = api.get_site_info(site_id)
        logger.info(f"Site info retrieved for: {site_id}")
        
        # Log retrieved site info for debugging
        logger.debug(f"Site Info Details: {site_info}")
        
        # Extract device details
        device_ids = [device['id'] for device in site_info.get('devices', [])]
        device_name_map = {device['id']: device['name'] for device in site_info.get('devices', [])}
        
        logger.info(f"Devices found: {device_ids}")
        
        # Cutoff date
        cutoff_date = datetime(2022, 1, 1, tzinfo=timezone.utc)
        
        # Filter outages
        filtered_outages = [
            {
                **outage,
                'name': device_name_map.get(outage['id'], '')
            }
            for outage in all_outages
            if (outage['id'] in device_ids and 
                datetime.fromisoformat(outage['begin'].replace('Z', '+00:00')).replace(tzinfo=timezone.utc) >= cutoff_date)
        ]
        
        logger.info(f"Filtered outages: {len(filtered_outages)}")
        return filtered_outages
    
    except Exception as e:
        logger.error(f"Outage processing error: {e}")
        raise

def main():
    """Main execution function with comprehensive error handling"""
    api_key = os.getenv('KRAKENFLEX_API_KEY')
    site_id = os.getenv('SITE_ID', 'norwich-pear-tree')
    
    if not api_key:
        logger.error("No API key found")
        return
    
    try:
        api = KrakenFlexAPI(api_key)
        filtered_outages = process_outages(api, site_id)
        
        # Post processed outages
        api.post_site_outages(site_id, filtered_outages)
        
        logger.info(f"Successfully processed {len(filtered_outages)} outages for {site_id}")
    
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise

if __name__ == "__main__":
    main()