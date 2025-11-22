import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_synthetic_data(num_rows=1000):
    """
    Generates a synthetic dataset of user health stats and run logs.
    """
    try:
        logging.info(f"Generating {num_rows} rows of synthetic data...")

        # Based on the analysis of the real data
        stats = {
            'TotalSteps': {'mean': 7637, 'std': 3794},
            'TotalDistance': {'mean': 5.48, 'std': 2.52},
            'VeryActiveMinutes': {'mean': 21, 'std': 20},
            'FairlyActiveMinutes': {'mean': 13, 'std': 15},
            'LightlyActiveMinutes': {'mean': 192, 'std': 88},
            'SedentaryMinutes': {'mean': 991, 'std': 301},
            'Calories': {'mean': 2303, 'std': 529},
            'TotalMinutesAsleep': {'mean': 419, 'std': 118},
            'TotalTimeInBed': {'mean': 458, 'std': 127},
            'RestingHeartRate': {'mean': 49, 'std': 5}
        }

        data = {}
        for col, prop in stats.items():
            data[col] = np.random.normal(prop['mean'], prop['std'], num_rows)

        # Ensure non-negative values for minutes, steps, etc.
        for col in data:
            data[col][data[col] < 0] = 0

        # Generate realistic IDs and dates
        num_users = num_rows // 10 # 100 users for 1000 rows
        user_ids = np.repeat(np.arange(1, num_users + 1), 10)
        data['Id'] = user_ids

        start_date = datetime(2024, 1, 1)
        dates = [start_date + timedelta(days=i) for i in range(num_rows)]
        data['ActivityDate'] = dates

        df = pd.DataFrame(data)

        # Reorder columns to match prepared_data.csv
        column_order = [
            'Id', 'ActivityDate', 'TotalSteps', 'TotalDistance',
            'VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes',
            'SedentaryMinutes', 'Calories', 'TotalMinutesAsleep',
            'TotalTimeInBed', 'RestingHeartRate'
        ]
        # Add missing columns with default values
        for col in column_order:
            if col not in df.columns:
                df[col] = 0
        df = df[column_order]


        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, 'synthetic_data.csv')
        df.to_csv(output_path, index=False)

        logging.info(f"Synthetic data saved to {output_path}")
        return output_path

    except Exception as e:
        logging.error(f"An error occurred during synthetic data generation: {e}")
        return None

if __name__ == '__main__':
    generate_synthetic_data()
