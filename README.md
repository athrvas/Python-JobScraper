# Web Scraping and Data Pipeline

This project is an automated pipeline for scraping job listings from websites. It extracts summary data, scrapes full job descriptions from detail pages, and stores the structured data in a PostgreSQL database for analysis.

## Technology Stack

  - **Language:** Python 3
  - **Database:** PostgreSQL
  - **Web Scraping:** Requests, BeautifulSoup, Selenium
  - **Task Automation:** GNU Make

## Features

  - Automated setup of the PostgreSQL database and table.
  - Scraping of job summaries from static web pages.
  - Scraping of full job descriptions from dynamic, JavaScript-rendered pages.
  - Secure credential management using a `.env` file.
  - Streamlined task execution via a `Makefile`.

-----

## Getting Started

Follow these instructions to get the project set up and running on your local machine.

### Prerequisites

  - Python 3.9 or later
  - A running PostgreSQL instance
  - `make` (pre-installed on macOS/Linux, requires installation on Windows)

### Setup and Installation

1.  **Clone the Repository**

    ```sh
    git clone https://github.com/athrvas/Python-JobScraper.git
    cd your-repository
    ```

2.  **Create and Activate a Virtual Environment**

    ```sh
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    This project uses a `requirements.txt` file to manage its packages.

    ```sh
    # If you haven't created the file yet, run this first:
    # pip freeze > requirements.txt

    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    The project uses a `.env` file to handle database credentials securely.

    ```sh
    # Copy the template to create your personal configuration file
    cp .env.example .env
    ```

    Now, open the newly created `.env` file and fill in your actual database credentials.

-----

## Usage

The `Makefile` provides commands to run the entire pipeline or individual parts.

  - **Run the full pipeline (setup -\> scrape -\> update):**
    ```sh
    make all
    ```
  - **Initialize the database and table:**
    ```sh
    make setup
    ```
  - **Scrape only the job summaries (Part 2):**
    ```sh
    make scrape
    ```
  - **Scrape only the job descriptions (Part 3):**
    ```sh
    make update
    ```

### Project Scripts

  - **`part1_setup.py`**: Initializes the database.
  - **`part2_scrape.py`**: Scrapes job summaries and saves them to the database.
  - **`part3_scrape_JD.py`**: Reads job URLs from the database, scrapes the full description, and updates the records.
  - **`config.py`**: Loads and manages the database configuration from the `.env` file.
