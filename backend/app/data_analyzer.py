import pandas as pd
from app.data_preparation import prepare_data
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_data():
    """
    Analyzes the prepared data to understand its statistical properties.
    """
    try:
        df = prepare_data()
        if df is None:
            logging.error("Failed to load prepared data.")
            return

        logging.info("--- Data Description ---")
        description = df.describe()
        logging.info(description)

        logging.info("\n--- Correlation Matrix ---")
        # Select only numeric columns for correlation calculation
        numeric_df = df.select_dtypes(include=['number'])
        correlation = numeric_df.corr()
        logging.info(correlation)

        # Save analysis results to a file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        analysis_results_path = os.path.join(script_dir, 'data_analysis_results.txt')
        with open(analysis_results_path, 'w') as f:
            f.write("--- Data Description ---\n")
            f.write(description.to_string())
            f.write("\n\n--- Correlation Matrix ---\n")
            f.write(correlation.to_string())
        logging.info(f"Analysis results saved to {analysis_results_path}")

    except Exception as e:
        logging.error(f"An error occurred during data analysis: {e}")

if __name__ == '__main__':
    analyze_data()
