"""
Database and table setup for the job scraping.
"""

import psycopg2
import sys
from config import DB_CONFIG, DB_HOST, DB_USER, DB_PASSWORD, DB_PORT

# --- Configuration ---

DB_TO_CREATE = "internship_assessment"

#Ensure the Database Exists ---
conn = None
try:
    # Connect to the default 'postgres' database to perform administrative tasks.
    print(f"Connecting to the default database to check for '{DB_TO_CREATE}'...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    conn.autocommit = True  # CREATE DATABASE requires autocommit mode.
    cur = conn.cursor()

    # Check if the target database already exists to avoid an error.
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_TO_CREATE,))
    if cur.fetchone():
        print(f"Database '{DB_TO_CREATE}' already exists.")
    else:
        # Create the database if it does not exist.
        cur.execute(f"CREATE DATABASE {DB_TO_CREATE}")
        print(f"Database '{DB_TO_CREATE}' created successfully.")

    cur.close()

except psycopg2.Error as e:
    print(f" Error during database setup: {e}")
    sys.exit(1)  # Exit the script if the database can't be created.

finally:
    # Ensure the connection is always closed, even if an error occurred.
    if conn is not None:
        conn.close()

# Ensure the Table Exists
conn = None
try:
    # Connect to the target database to create the table.
    print(f"\nConnecting to '{DB_TO_CREATE}' to set up the table...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_TO_CREATE,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cur = conn.cursor()

    # Define the table structure. Using IF NOT EXISTS prevents errors on re-runs.
    create_table_query = """CREATE TABLE IF NOT EXISTS job_listings (
        id SERIAL PRIMARY KEY,
        job_title VARCHAR(255),
        company_name VARCHAR(255),
        location VARCHAR(255),
        job_url VARCHAR(512) UNIQUE,
        salary_info TEXT,
        job_description TEXT,
        source_site VARCHAR(100),
        scraped_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );"""

    cur.execute(create_table_query)
    print("Table 'job_listings' is ready.")

    # Commit the transaction to make the changes permanent.
    conn.commit()
    cur.close()

except psycopg2.Error as e:
    print(f"Error during table creation: {e}")
    sys.exit(1)

finally:
    if conn is not None:
        conn.close()

print("\nDatabase and table setup completed successfully.")