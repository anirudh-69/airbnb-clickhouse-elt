import gzip
import shutil
import dlt
import subprocess
import os
import logging
from typing import Optional
import pandas as pd

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_and_unzip(url: str, filename: str, directory: str) -> Optional[str]:
    """Downloads the .gz file, unzips it, and returns the path to the csv file."""
    os.makedirs(directory, exist_ok=True)
    gz_path = os.path.join(directory, filename)
    csv_path = os.path.splitext(gz_path)[0]

    try:
        subprocess.run(["wget", "-O", gz_path, url], check=True, capture_output=True, text=True)
        logger.info(f"Downloaded: {url}")

        with gzip.open(gz_path, "rt", encoding='utf-8') as f_in, open(csv_path, "wt", encoding='utf-8') as f_out:
            shutil.copyfileobj(f_in, f_out)
        logger.info(f"Unzipped: {filename}")
        return csv_path
    except Exception as e:
        logger.exception(f"Unzip failed: {filename} - {e}")
        return None

def load_table(pipeline, csv_path: str, table_name: str) -> bool:
    """Loads the CSV file into Clickhouse, using the headers as column names."""
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        resource = dlt.resource(df, name=table_name)

        info = pipeline.run(resource, table_name=table_name, write_disposition="replace")
        logger.info(f"Loaded {table_name}: {info}")
        return True
    except Exception as e:
        logger.error(f"Failed to load {table_name}: {e}")
        return False

if __name__ == "__main__":
    pipeline = dlt.pipeline(pipeline_name="airbnb", destination="clickhouse")
    base_url = "https://data.insideairbnb.com/united-states/ny/new-york-city/2025-01-03/data"
    data_dir = "data"

    tables = {
        "listings": f"{base_url}/listings.csv.gz",
        "reviews": f"{base_url}/reviews.csv.gz"
    }

    for table_name, url in tables.items():
        if csv_path := download_and_unzip(url, f"{table_name}.csv.gz", data_dir):
            load_table(pipeline, csv_path, table_name)

    logger.info("Airbnb pipeline finished.")