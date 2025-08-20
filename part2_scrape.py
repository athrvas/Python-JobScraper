"""
Part 2: Robust Job Scraper for WeWorkRemotely
Handles multiple HTML structures for job listings.
"""

import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin
import sys
import requests
from bs4 import BeautifulSoup, Tag
import psycopg2
from psycopg2.extras import execute_values
from config import DB_CONFIG

# --- Boilerplate Code (Logging and DatabaseManager Class) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages the database connection and operations."""

    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("Database connection established.")
            return self
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            sys.exit(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")

    def bulk_insert_jobs(self, jobs: List[Dict]) -> int:
        """Inserts a list of jobs using a fast, single transaction."""
        if not jobs: return 0
        job_tuples = [(j.get('job_title'), j.get('company_name'), j.get('location'),
                       j.get('job_url'), j.get('salary_info'), j.get('source_site')) for j in jobs]
        sql = "INSERT INTO job_listings (job_title, company_name, location, job_url, salary_info, source_site) VALUES %s ON CONFLICT (job_url) DO NOTHING;"
        try:
            with self.conn.cursor() as cursor:
                execute_values(cursor, sql, job_tuples)
                count = cursor.rowcount
                self.conn.commit()
                return count
        except psycopg2.Error as e:
            logger.error(f"Database bulk insert error: {e}")
            self.conn.rollback()
            return 0


# --- Job Scraper---
class JobScraper:
    """Scrapes job data using requests and BeautifulSoup."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        self.base_url = "https://weworkremotely.com"

    def _extract_text(self, soup_item: Tag, selector: str) -> Optional[str]:
        """Safely extracts text from an element found by a CSS selector."""
        element = soup_item.select_one(selector)
        return element.get_text(strip=True) if element else None

    def _find_salary(self, soup_item: Tag) -> Optional[str]:
        """Specifically looks for salary information in the new listing format."""
        categories_div = soup_item.select_one('div.new-listing__categories')
        if not categories_div:
            return None

        for category in categories_div.select('p.new-listing__categories__category'):
            text = category.get_text()
            if '$' in text or 'USD' in text:
                return text.strip()
        return None

    def _find_job_link(self, soup_item: Tag) -> Optional[str]:
        """
        Finds the correct job post link by searching for a URL containing '/remote-jobs/'.
        """
        all_links = soup_item.find_all('a', href=True)
        for link in all_links: #filter the job specific links from multiple links
            if '/remote-jobs/' in link['href']:
                return link['href']
        return None

    def scrape_weworkremotely(self, url: str) -> List[Dict]:
        """
        Scrapes all job listings, handling both standard and "new" HTML formats.
        """
        all_jobs = []
        logger.info(f"Scraping jobs from: {url}")

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            job_listings = soup.select('section#category-2 li')
            logger.info(f"Found {len(job_listings)} total job list items.")

            for item in job_listings:
                # Use the new, more reliable method to find the job URL
                job_path = self._find_job_link(item)
                if not job_path:
                    continue  # Skip if no valid job link is found

                job_url = urljoin(self.base_url, job_path)

                # Extract other data using the robust multi-selector approach
                job_title = self._extract_text(item, 'h4.new-listing__header__title') or self._extract_text(item,
                                                                                                            'span.title')
                company = self._extract_text(item, 'p.new-listing__company-name') or self._extract_text(item,
                                                                                                        'span.company')
                location = self._extract_text(item, 'p.new-listing__company-headquarters') or self._extract_text(item,
                                                                                                                 'span.region')
                salary = self._find_salary(item)

                if job_title and company:
                    all_jobs.append({
                        'job_title': job_title,
                        'company_name': company,
                        'location': location or "Remote",
                        'job_url': job_url,
                        'salary_info': salary,
                        'source_site': 'WeWorkRemotely'
                    })

        except requests.RequestException as e:
            logger.error(f"Request to {url} failed: {e}")

        return all_jobs
def main():
    """Main function to run the scraping and insertion process."""

    target_url = "https://weworkremotely.com/categories/remote-full-stack-programming-jobs"
    scraper = JobScraper()

    with DatabaseManager(DB_CONFIG) as db:
        jobs_to_insert = scraper.scrape_weworkremotely(target_url)
        if not jobs_to_insert:
            logger.warning("No jobs were found.")
            return

        logger.info(f"Attempting to insert {len(jobs_to_insert)} jobs into the database...")
        inserted_count = db.bulk_insert_jobs(jobs_to_insert)

        print("\n" + "=" * 60)
        print("JOB SCRAPING COMPLETED!")
        print("=" * 60)
        print(f"Jobs found on page: {len(jobs_to_insert)}")
        print(f"New jobs inserted into database: {inserted_count}")
        print("=" * 60)


if __name__ == "__main__":
    main()