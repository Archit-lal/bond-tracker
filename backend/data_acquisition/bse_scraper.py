import requests
import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class BSEScraper:
    """
    Class to scrape bond data from BSE website.
    """
    # Base URL for BSE debt search
    BASE_URL = "https://www.bseindia.com/markets/debt/debt_search.aspx"
    SEARCH_URL = "https://www.bseindia.com/markets/debt/debt_search_result.aspx"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.bseindia.com/markets/debt/debt_search.aspx',
            'Origin': 'https://www.bseindia.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make HTTP request to BSE website with retry mechanism.
        """
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                # First visit the search page to get cookies
                self.session.get(self.BASE_URL)
                
                # Then make the actual request
                if data:
                    response = self.session.post(url, data=data, params=params, timeout=30)
                else:
                    response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay * (attempt + 1))

    def fetch_bond_data(self, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """
        Fetch bond data for a given date range from BSE's debt search page.
        """
        logger.info(f"Fetching bond data from BSE for date range: {from_date} to {to_date}")
        
        # Prepare form data for POST request
        data = {
            'ctl00$ContentPlaceHolder1$txtFromDate': from_date,
            'ctl00$ContentPlaceHolder1$txtToDate': to_date,
            'ctl00$ContentPlaceHolder1$btnSubmit': 'Submit'
        }
        
        try:
            response = self._make_request(self.SEARCH_URL, data=data)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the table containing bond data
            table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_gvDebt'})
            if not table:
                logger.warning("No bond data table found in BSE response")
                return []

            transactions = []
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 8:  # Ensure we have all required columns
                    try:
                        # Clean and parse numeric values
                        def clean_numeric(value: str) -> float:
                            return float(value.strip().replace(',', '')) if value.strip() else 0.0
                        
                        def clean_volume(value: str) -> int:
                            return int(value.strip().replace(',', '')) if value.strip() else 0

                        transaction = {
                            'isin': cols[0].text.strip(),
                            'date': cols[1].text.strip(),
                            'open': clean_numeric(cols[2].text),
                            'high': clean_numeric(cols[3].text),
                            'low': clean_numeric(cols[4].text),
                            'close': clean_numeric(cols[5].text),
                            'volume': clean_volume(cols[6].text),
                            'source': 'BSE'
                        }
                        transactions.append(transaction)
                    except (ValueError, IndexError) as e:
                        logger.error(f"Error parsing row data: {e}")
                        continue

            logger.info(f"Successfully fetched {len(transactions)} transactions from BSE for date range: {from_date} to {to_date}")
            return transactions
        except Exception as e:
            logger.error(f"Failed to fetch bond data from BSE for date range {from_date} to {to_date}: {e}")
            return []

# Example usage
if __name__ == "__main__":
    scraper = BSEScraper()
    from_date = "01-01-2023"
    to_date = "31-12-2023"
    transactions = scraper.fetch_bond_data(from_date, to_date)
    print(transactions) 