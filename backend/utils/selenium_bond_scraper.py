import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from sqlalchemy.orm import Session
from database.models import Bond, Transaction, Exchange
from database.session import SessionLocal
import csv
from io import StringIO
from selenium.webdriver.chrome.service import Service
import os
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIG ---
NSE_URL = "https://www.nseindia.com/historical/security-wise-trades-data"
BSE_URL = "https://www.bseindia.com/markets/debt/debt_search.aspx"
WAIT_TIMEOUT = 30  # seconds

# --- UTILS ---
def get_headless_chrome():
    options = ChromeOptions()
    options.add_argument('--headless=new')  # Use new headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Use environment variables for Chrome binary and driver paths
    chrome_bin = os.getenv('CHROME_BIN', '/usr/bin/chromium')
    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
    
    options.binary_location = chrome_bin
    
    try:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome driver: {str(e)}")
        logger.error(f"Chrome binary path: {chrome_bin}")
        logger.error(f"ChromeDriver path: {chromedriver_path}")
        raise

def wait_for_element(driver, by, value, timeout=WAIT_TIMEOUT):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        logger.error(f"Timeout waiting for element: {value}")
        raise

def upsert_bond_and_transaction(db: Session, bond_data: dict, txn_data: dict):
    try:
        bond = db.query(Bond).filter(Bond.isin == bond_data['isin']).first()
        if not bond:
            bond = Bond(**bond_data)
            db.add(bond)
            db.commit()
            db.refresh(bond)
            logger.info(f"Created new bond: {bond_data['isin']}")
        
        # Check for duplicate transaction
        exists = db.query(Transaction).filter(
            Transaction.bond_id == bond.id,
            Transaction.timestamp == txn_data['timestamp']
        ).first()
        
        if not exists:
            txn = Transaction(bond_id=bond.id, **txn_data)
            db.add(txn)
            db.commit()
            logger.info(f"Added new transaction for bond: {bond_data['isin']}")
    except Exception as e:
        logger.error(f"Error upserting bond/transaction: {str(e)}")
        db.rollback()
        raise

# --- BSE SCRAPER ---
def scrape_bse_bonds(fetch_all=True, last_run_time=None):
    driver = None
    try:
        driver = get_headless_chrome()
        logger.info("Starting BSE bond scraping")
        
        # Set a realistic user agent
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        logger.info("Navigating to BSE URL")
        driver.get(BSE_URL)
        time.sleep(10)  # Increased initial page load wait time
        
        # Log page title and URL to verify we're on the right page
        logger.info(f"Current page title: {driver.title}")
        logger.info(f"Current URL: {driver.current_url}")
        
        # Wait for and click the primary market radio button
        logger.info("Looking for primary market radio button")
        primary_market_radio = wait_for_element(driver, By.ID, "ContentPlaceHolder1_rdbtrp")
        primary_market_radio.click()
        logger.info("Clicked primary market radio button")
        
        # Set date range to 6 months ago to today
        from_date = (datetime.now() - timedelta(days=180)).strftime("%d/%m/%Y")
        to_date = datetime.now().strftime("%d/%m/%Y")
        
        logger.info(f"Setting date range: {from_date} to {to_date}")
        
        # Wait for page to stabilize after radio button click
        time.sleep(5)
        
        # Fill date fields with retry logic
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Try to find date inputs using multiple possible selectors
                date_selectors = [
                    (By.ID, "ContentPlaceHolder1_txtFromDate"),
                    (By.NAME, "ctl00$ContentPlaceHolder1$txtFromDate"),
                    (By.CSS_SELECTOR, "input[type='text'][name*='txtFromDate']")
                ]
                
                from_date_input = None
                for by, selector in date_selectors:
                    try:
                        from_date_input = wait_for_element(driver, by, selector, timeout=20)
                        if from_date_input:
                            break
                    except:
                        continue
                
                if not from_date_input:
                    raise Exception("Could not find from date input field")
                
                from_date_input.clear()
                from_date_input.send_keys(from_date)
                logger.info("Set from date")
                
                # Wait between date inputs
                time.sleep(2)
                
                # Try to find to date input using multiple possible selectors
                to_date_selectors = [
                    (By.ID, "ContentPlaceHolder1_txtTodate"),
                    (By.NAME, "ctl00$ContentPlaceHolder1$txtTodate"),
                    (By.CSS_SELECTOR, "input[type='text'][name*='txtTodate']")
                ]
                
                to_date_input = None
                for by, selector in to_date_selectors:
                    try:
                        to_date_input = wait_for_element(driver, by, selector, timeout=20)
                        if to_date_input:
                            break
                    except:
                        continue
                
                if not to_date_input:
                    raise Exception("Could not find to date input field")
                
                to_date_input.clear()
                to_date_input.send_keys(to_date)
                logger.info("Set to date")
                
                # If we get here, both date inputs were successful
                break
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count} failed to set date inputs: {str(e)}")
                if retry_count == max_retries:
                    raise Exception(f"Failed to set date inputs after {max_retries} attempts: {str(e)}")
                time.sleep(5)  # Wait before retry
        
        # Submit form with retry logic
        submit_retries = 3
        submit_count = 0
        
        while submit_count < submit_retries:
            try:
                logger.info("Looking for submit button")
                submit_button = wait_for_element(driver, By.ID, "ContentPlaceHolder1_btnSubmit")
                
                # Wait for any JavaScript to complete
                time.sleep(2)
                
                # Try to click the submit button
                try:
                    submit_button.click()
                    logger.info("Clicked submit button")
                except Exception as click_error:
                    # If direct click fails, try JavaScript click
                    logger.warning(f"Direct click failed, trying JavaScript click: {str(click_error)}")
                    driver.execute_script("arguments[0].click();", submit_button)
                    logger.info("Executed JavaScript click on submit button")
                
                # Wait for form submission and page load
                time.sleep(10)  # Increased wait time
                
                # Wait for the results table to appear
                try:
                    logger.info("Waiting for results table - this may take a few minutes...")
                    # First check if there's a loading indicator
                    try:
                        loading_indicator = driver.find_element(By.ID, "ContentPlaceHolder1_UpdateProgress1")
                        if loading_indicator.is_displayed():
                            logger.info("Loading indicator visible - waiting for data to load...")
                    except NoSuchElementException:
                        logger.info("No loading indicator found")
                    
                    # Wait longer for the table
                    table = wait_for_element(driver, By.ID, "ContentPlaceHolder1_gvDebt", timeout=180)  # Increased timeout to 3 minutes
                    logger.info("Found results table")
                    
                    # Check if table has data
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 1:  # More than just header row
                        logger.info(f"Table has {len(rows)-1} rows of data")
                    else:
                        logger.warning("Table appears to be empty")
                    
                    # Wait a bit more for any dynamic content to load
                    time.sleep(5)
                    
                    # Now look for the export button
                    logger.info("Looking for export button")
                    export_button = wait_for_element(driver, By.ID, "ContentPlaceHolder1_btnExport", timeout=30)
                    logger.info("Found export button")
                    
                    # Click the export button
                    try:
                        export_button.click()
                        logger.info("Clicked export button")
                    except Exception as click_error:
                        logger.warning(f"Direct click failed, trying JavaScript click: {str(click_error)}")
                        driver.execute_script("arguments[0].click();", export_button)
                        logger.info("Executed JavaScript click on export button")
                    
                    # Wait for download to complete
                    time.sleep(5)
                    
                    # Get the table content
                    table_content = table.get_attribute("outerHTML")
                    
                    # Parse table content
                    bse_data = []
                    soup = BeautifulSoup(table_content, 'html.parser')
                    rows = soup.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        try:
                            cols = row.find_all('td')
                            if len(cols) >= 8:
                                isin = cols[0].text.strip()
                                date_str = cols[1].text.strip()
                                timestamp = datetime.strptime(date_str, '%d/%m/%Y')
                                price = float(cols[5].text.strip().replace(',', '')) if cols[5].text.strip() else 0.0
                                quantity = int(cols[6].text.strip().replace(',', '')) if cols[6].text.strip() else 0
                                
                                bond_data = {
                                    'isin': isin,
                                    'name': cols[2].text.strip() or f"Bond {isin}",
                                    'issuer': cols[3].text.strip() or "Unknown",
                                    'exchange': Exchange.BSE,
                                    'face_value': 100.0,
                                    'coupon_rate': 0.0,
                                    'maturity_date': datetime.now() + timedelta(days=365*5),
                                    'yield_to_maturity': 0.0,
                                    'last_price': price,
                                    'volume': quantity
                                }
                                
                                txn_data = {
                                    'timestamp': timestamp,
                                    'price': price,
                                    'quantity': quantity
                                }
                                
                                bse_data.append((bond_data, txn_data))
                                logger.info(f"Successfully parsed bond: {isin}")
                        except Exception as e:
                            logger.error(f"Error parsing BSE row: {str(e)}")
                            continue
                    
                    logger.info(f"Successfully scraped {len(bse_data)} bonds from BSE")
                    return bse_data
                    
                except Exception as table_error:
                    logger.error(f"Error finding results table: {str(table_error)}")
                    raise
                
            except Exception as e:
                submit_count += 1
                logger.warning(f"Submit attempt {submit_count} failed: {str(e)}")
                if submit_count == submit_retries:
                    raise Exception(f"Failed to submit form after {submit_retries} attempts: {str(e)}")
                time.sleep(5)  # Wait before retry
        
    except Exception as e:
        logger.error(f"Error in BSE scraping: {str(e)}")
        if driver:
            logger.error(f"Page source at time of error: {driver.page_source}")
        raise
    finally:
        if driver:
            driver.quit()

# --- NSE SCRAPER ---
def scrape_nse_for_isin(isin, fetch_all=True, last_run_time=None):
    driver = None
    try:
        driver = get_headless_chrome()
        logger.info(f"Starting NSE scraping for ISIN: {isin}")
        
        driver.get(NSE_URL)
        time.sleep(2)  # Initial page load
        
        # Enter ISIN
        isin_input = wait_for_element(driver, By.ID, "hpReportISINSearchInput")
        isin_input.clear()
        isin_input.send_keys(isin)
        time.sleep(1)
        
        # Set date range if needed
        if not fetch_all and last_run_time:
            # TODO: Implement date range selection
            pass
        
        # Click download button
        download_button = wait_for_element(driver, By.ID, "CFanncEquity-download")
        download_button.click()
        time.sleep(5)
        
        # Scrape table
        table = wait_for_element(driver, By.CSS_SELECTOR, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
        
        nse_data = []
        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 7:
                    date_str = cols[0].text.strip()
                    timestamp = datetime.strptime(date_str, '%d-%b-%Y')
                    price = float(cols[1].text.strip().replace(',', '')) if cols[1].text.strip() else 0.0
                    quantity = int(cols[3].text.strip().replace(',', '')) if cols[3].text.strip() else 0
                    
                    bond_data = {
                        'isin': isin,
                        'name': '',  # Will be filled from BSE
                        'issuer': '',
                        'exchange': Exchange.NSE,
                        'face_value': 100.0,
                        'coupon_rate': 0.0,
                        'maturity_date': datetime.now() + timedelta(days=365*5),
                        'yield_to_maturity': 0.0,
                        'last_price': price,
                        'volume': quantity
                    }
                    
                    txn_data = {
                        'timestamp': timestamp,
                        'price': price,
                        'quantity': quantity
                    }
                    
                    nse_data.append((bond_data, txn_data))
            except Exception as e:
                logger.error(f"Error parsing NSE row: {str(e)}")
                continue
        
        logger.info(f"Successfully scraped {len(nse_data)} transactions from NSE for ISIN: {isin}")
        return nse_data
        
    except Exception as e:
        logger.error(f"Error in NSE scraping for ISIN {isin}: {str(e)}")
        raise
    finally:
        if driver:
            driver.quit()

# --- MAIN ORCHESTRATOR ---
def run_selenium_scraper(fetch_all=True, last_run_time=None):
    db = SessionLocal()
    try:
        logger.info("Starting bond data scraping process")
        
        # 1. Scrape BSE for all ISINs and bond transactions
        bse_data = scrape_bse_bonds(fetch_all=fetch_all, last_run_time=last_run_time)
        isins = set()
        
        # First pass: Store all BSE data
        for bond_data, txn_data in bse_data:
            try:
                # Store BSE data
                upsert_bond_and_transaction(db, bond_data, txn_data)
                isins.add(bond_data['isin'])
                logger.info(f"Stored BSE data for ISIN: {bond_data['isin']}")
            except Exception as e:
                logger.error(f"Error processing BSE data for ISIN {bond_data['isin']}: {str(e)}")
                continue
        
        # 2. For each ISIN, fetch and store NSE data
        for isin in isins:
            try:
                logger.info(f"Fetching NSE data for ISIN: {isin}")
                nse_data = scrape_nse_for_isin(isin, fetch_all=fetch_all, last_run_time=last_run_time)
                
                # Get the bond from database to update with NSE data
                bond = db.query(Bond).filter(Bond.isin == isin).first()
                if not bond:
                    logger.warning(f"Bond not found in database for ISIN: {isin}")
                    continue
                
                # Update bond with NSE data if available
                if nse_data:
                    latest_nse_data = nse_data[0][0]  # Get the first bond data entry
                    bond.last_price = latest_nse_data['last_price']
                    bond.volume = latest_nse_data['volume']
                    bond.exchange = Exchange.NSE  # Update exchange to NSE if we have NSE data
                    db.commit()
                    logger.info(f"Updated bond with NSE data for ISIN: {isin}")
                
                # Store NSE transactions
                for bond_data, txn_data in nse_data:
                    try:
                        # Use the existing bond ID
                        txn_data['bond_id'] = bond.id
                        txn = Transaction(**txn_data)
                        db.add(txn)
                        db.commit()
                        logger.info(f"Added NSE transaction for ISIN: {isin}")
                    except Exception as e:
                        logger.error(f"Error storing NSE transaction for ISIN {isin}: {str(e)}")
                        db.rollback()
                        continue
                
            except Exception as e:
                logger.error(f"Error processing NSE data for ISIN {isin}: {str(e)}")
                continue
        
        # 3. Update bond statistics
        for isin in isins:
            try:
                bond = db.query(Bond).filter(Bond.isin == isin).first()
                if bond:
                    # Get latest transaction
                    latest_txn = db.query(Transaction).filter(
                        Transaction.bond_id == bond.id
                    ).order_by(Transaction.timestamp.desc()).first()
                    
                    if latest_txn:
                        bond.last_price = latest_txn.price
                        bond.volume = latest_txn.quantity
                        db.commit()
                        logger.info(f"Updated bond statistics for ISIN: {isin}")
            except Exception as e:
                logger.error(f"Error updating bond statistics for ISIN {isin}: {str(e)}")
                continue
        
        logger.info("Successfully completed bond data scraping process")
        
    except Exception as e:
        logger.error(f"Error in main scraping process: {str(e)}")
        raise
    finally:
        db.close()

# Add a function to check for new data
def check_for_updates():
    """
    Check for new data since last run and update the database.
    This function should be called periodically (e.g., every hour).
    """
    try:
        # Get the timestamp of the last successful run
        last_run = get_last_run_time()  # You'll need to implement this
        run_selenium_scraper(fetch_all=False, last_run_time=last_run)
    except Exception as e:
        logger.error(f"Error checking for updates: {str(e)}")
        raise

# Add a function to get the last run time
def get_last_run_time():
    """
    Get the timestamp of the last successful data fetch.
    This could be stored in a database or file.
    """
    try:
        # For now, return 1 hour ago
        return datetime.now() - timedelta(hours=1)
    except Exception as e:
        logger.error(f"Error getting last run time: {str(e)}")
        return None

# Example usage:
# run_selenium_scraper(fetch_all=True)
# For hourly update: run_selenium_scraper(fetch_all=False, last_run_time=datetime.now() - timedelta(hours=1)) 