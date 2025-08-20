# Makefile for the Job Scraper Project
# Defines common tasks for the project.

# Phony targets are not actual files, they are just commands
.PHONY: all setup scrape update

# The 'all' command runs the entire pipeline in order
all: setup scrape update

# Sets up the database and table
setup:
	@echo "--- 1. Setting up the database... ---"
	python part1_setup.py

# Scrapes the summary job listings
scrape:
	@echo "--- 2. Scraping job summaries... ---"
	python part2_scrape.py

# Updates the database with full job descriptions
update:
	@echo "--- 3. Scraping full job descriptions... ---"
	python part3_scrape_JD.py