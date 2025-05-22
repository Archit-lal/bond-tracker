from celery import Celery
from data_acquisition.nse_scraper import NSEScraper
from data_acquisition.bse_scraper import BSEScraper
from database.session import SessionLocal
from database.models import Bond, Transaction, Exchange
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from utils.selenium_bond_scraper import run_selenium_scraper, check_for_updates
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    'bond_dashboard',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True, max_retries=3)
def fetch_bond_data(self):
    """
    Celery task to fetch bond data from NSE and BSE.
    This task will:
    1. Do a full fetch if no data exists
    2. Otherwise, fetch only new data since last run
    """
    db = SessionLocal()
    try:
        # Check if we have any data
        bond_count = db.query(Bond).count()
        
        if bond_count == 0:
            logger.info("No existing data found. Performing full data fetch.")
            run_selenium_scraper(fetch_all=True)
        else:
            logger.info("Existing data found. Checking for updates.")
            check_for_updates()
            
        logger.info("Successfully completed bond data fetch task")
        
    except Exception as e:
        logger.error(f"Error in bond data fetch task: {str(e)}")
        # Retry the task with exponential backoff
        retry_in = (2 ** self.request.retries) * 60  # minutes
        self.retry(exc=e, countdown=retry_in)
    finally:
        db.close()

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    'fetch-bond-data-hourly': {
        'task': 'celery_app.fetch_bond_data',
        'schedule': 3600.0,  # Run every hour
    },
}

# Example usage:
# To start the worker: celery -A celery_app worker --loglevel=info
# To start the beat scheduler: celery -A celery_app beat --loglevel=info 