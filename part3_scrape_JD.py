#!/usr/bin/env python3
"""
Part 3: Scraping Job Descriptions with Selenium (Refactored)

This script reads job entries from a PostgreSQL database, navigates to each
job's detail page, scrapes the full job description based on a configurable
selector, and updates the database record.
"""

import logging
import sys
import time
import os
from typing import List, Dict

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException
from config import DB_CONFIG

# Database imports
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseManager:
    """Manages all database interactions for this script."""

    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            return self
        except psycopg2.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            sys.exit(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()


    def get_jobs_to_update(self, limit: int = None) -> List[Dict]:
        """
        Fetches jobs that have a NULL or an empty string description.
        """
        # This query finds both NULLs and empty strings.
        query = "SELECT id, job_url FROM job_listings WHERE job_description IS NULL OR trim(job_description) = '' ORDER BY id"

        if limit:
            query += f" LIMIT {limit}"
        query += ";"

        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def update_description(self, job_id: int, description: str):
        """Updates a specific job row with the scraped description."""
        update_sql = "UPDATE job_listings SET job_description = %s WHERE id = %s;"
        with self.conn.cursor() as cursor:
            cursor.execute(update_sql, (description, job_id))
        self.conn.commit()


def setup_driver():
    """Set up and return a headless Selenium Firefox WebDriver."""
    options = FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver


def scrape_full_description(driver, url: str, selector: str) -> str | None:
    """
    Navigates to a job detail URL and extracts the full description text
    using a provided CSS selector.
    """
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        description_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return description_element.text
    except TimeoutException:
        logging.warning(f"Timeout: Description element ('{selector}') not found on {url}")
        return None
    except Exception as e:
        logging.error(f"An error occurred scraping description from {url}: {e}")
        return None


def main():
    """Main function to run the description scraping process."""

    # --- Configuration ---

    DESCRIPTION_SELECTOR = "div.lis-container__job__content__description"

    # Set a limit for testing, or set to None to run on all jobs.
    JOB_LIMIT = None
    # --- End of Configuration ---

    with DatabaseManager(DB_CONFIG) as db:
        jobs_to_update = db.get_jobs_to_update(JOB_LIMIT)

        if not jobs_to_update:
            logging.info("All jobs in the database already have a description. No work to do.")
            return

        logging.info(f"Found {len(jobs_to_update)} jobs to process. Initializing scraper...")
        driver = setup_driver()
        updated_count = 0

        try:
            for i, job in enumerate(jobs_to_update, 1):
                logging.info(f"[{i}/{len(jobs_to_update)}] Processing Job ID: {job['id']}")
                # Pass the selector from the config to the scraping function
                description = scrape_full_description(driver, job['job_url'], DESCRIPTION_SELECTOR)

                if description:
                    db.update_description(job['id'], description)
                    logging.info(f"Successfully updated Job ID: {job['id']}")
                    updated_count += 1
                else:
                    logging.warning(f"Skipping update for Job ID: {job['id']} due to missing description.")

                time.sleep(2)
        finally:
            logging.info("Closing WebDriver...")
            driver.quit()

        # --- Final Summary ---
        print("\n" + "=" * 60)
        print("DESCRIPTION SCRAPING COMPLETED!")
        print("=" * 60)
        print(f"Jobs processed: {len(jobs_to_update)}")
        print(f"Successfully updated: {updated_count}")
        print("=" * 60)


if __name__ == "__main__":
    main()