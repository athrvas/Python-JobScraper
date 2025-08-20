import os
import sys
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'internship_assessment')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD')

DB_CONFIG = {
    'host': DB_HOST,
    'port': DB_PORT,
    'database': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD
}

if DB_PASSWORD is None:
    print("ERROR: DB_PASSWORD not found.")
    print("Please ensure you have a .env file with your DB_PASSWORD.")
    sys.exit(1)