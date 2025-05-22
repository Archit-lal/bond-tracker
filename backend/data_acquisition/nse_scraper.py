import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class NSEScraper:
    """
    Class to scrape bond data from NSE website.
    """
    # Base URL for NSE historical data
    BASE_URL = "https://www.nseindia.com/api/historical/security-wise-trades"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="91", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        })

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make HTTP request to NSE website with retry mechanism.
        """
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                # First visit the main page to get cookies
                self.session.get('https://www.nseindia.com/')
                
                # Then make the actual request
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay * (attempt + 1))

    def fetch_bond_data(self, isin: str) -> List[Dict[str, Any]]:
        """
        Fetch bond data for a given ISIN from NSE's historical data page.
        """
        logger.info(f"Fetching bond data from NSE for ISIN: {isin}")
        
        # Calculate date range (last 30 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        params = {
            'symbol': isin,
            'segmentLink': '13',  # Debt segment
            'symbolCount': '1',
            'series': 'ALL',
            'dateRange': '30days',
            'fromDate': from_date.strftime('%d-%m-%Y'),
            'toDate': to_date.strftime('%d-%m-%Y'),
            'dataType': 'PRICE'
        }
        
        try:
            response = self._make_request(self.BASE_URL, params)
            data = response.json()
            
            if not data or 'data' not in data:
                logger.warning(f"No data found for ISIN {isin}")
                return []

            transactions = []
            for item in data['data']:
                try:
                    # Parse date string
                    date_str = item.get('date', '')
                    if date_str:
                        try:
                            trade_date = datetime.strptime(date_str, '%d-%b-%Y')
                        except ValueError:
                            trade_date = None
                    else:
                        trade_date = None

                    transaction = {
                        'isin': isin,
                        'date': date_str,
                        'open': float(item.get('open', 0)),
                        'high': float(item.get('high', 0)),
                        'low': float(item.get('low', 0)),
                        'close': float(item.get('close', 0)),
                        'volume': int(item.get('volume', 0)),
                        'source': 'NSE'
                    }
                    transactions.append(transaction)
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing transaction data: {e}")
                    continue

            logger.info(f"Successfully fetched {len(transactions)} transactions from NSE for ISIN: {isin}")
            return transactions
        except Exception as e:
            logger.error(f"Failed to fetch bond data from NSE for ISIN {isin}: {e}")
            return []

# Example usage
if __name__ == "__main__":
    scraper = NSEScraper()
    isin = "INE001A07BM4"  # Example ISIN
    transactions = scraper.fetch_bond_data(isin)
    print(transactions) 