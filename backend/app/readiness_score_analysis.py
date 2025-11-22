import pandas as pd
import os
from sklearn.impute import KNNImputer

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up two levels to the project root
project_root = os.path.dirname(os.path.dirname(script_dir))

# Construct the paths to the data files
daily_activity_path = os.path.join(project_root, 'dataset', 'mturkfitbit_export_4.12.16-5.12.16', 'Fitabase Data 4.12.16-5.12.16', 'dailyActivity_merged.csv')
sleep_day_path = os.path.join(project_root, 'dataset', 'mturkfitbit_export_4.12.16-5.12.16', 'Fitabase Data 4.12.16-5.12.16', 'sleepDay_merged.csv')
heart_rate_path = os.path.join(project_root, 'dataset', 'mturkfitbit_export_4.12.16-5.12.16', 'Fitabase Data 4.12.16-5.12.16', 'heartrate_seconds_merged.csv')
results_path = os.path.join(script_dir, 'readiness_score_results.txt')


# Load the datasets
daily_activity = pd.read_csv(daily_activity_path)
sleep_day = pd.read_csv(sleep_day_path)

# Clean up the column names
daily_activity.columns = daily_activity.columns.str.strip()
sleep_day.columns = sleep_day.columns.str.strip()

# Convert date columns to datetime objects
daily_activity['ActivityDate'] = pd.to_datetime(daily_activity['ActivityDate'], format='%m/%d/%Y')
sleep_day['SleepDay'] = pd.to_datetime(sleep_day['SleepDay'], format='%m/%d/%Y %I:%M:%S %p').dt.date
sleep_day['SleepDay'] = pd.to_datetime(sleep_day['SleepDay'])

print("Daily activity date range:", daily_activity['ActivityDate'].min(), "to", daily_activity['ActivityDate'].max())
print("Sleep day date range:", sleep_day['SleepDay'].min(), "to", sleep_day['SleepDay'].max())


# Merge the two dataframes
merged_data = pd.merge(daily_activity, sleep_day, left_on=['Id', 'ActivityDate'], right_on=['Id', 'SleepDay'])

# --- Data Cleaning ---
# Remove duplicates
merged_data.drop_duplicates(inplace=True)



# --- Resting Heart Rate Calculation ---

# Create a dictionary to store resting heart rate for each user and date
resting_heart_rates = {}

# Process heart rate data in chunks
heart_rate_chunk_size = 100000
heart_rate_reader = pd.read_csv(heart_rate_path, chunksize=heart_rate_chunk_size)

print("Processing heart rate data...")
min_hr_date = None
max_hr_date = None

for i, heart_rate_chunk in enumerate(heart_rate_reader):
    # Convert 'Time' column to datetime objects
    heart_rate_chunk['Time'] = pd.to_datetime(heart_rate_chunk['Time'], format='%m/%d/%Y %I:%M:%S %p')
    heart_rate_chunk['Date'] = heart_rate_chunk['Time'].dt.date

    if min_hr_date is None:
        min_hr_date = heart_rate_chunk['Date'].min()
    else:
        min_hr_date = min(min_hr_date, heart_rate_chunk['Date'].min())

    if max_hr_date is None:
        max_hr_date = heart_rate_chunk['Date'].max()
    else:
        max_hr_date = max(max_hr_date, heart_rate_chunk['Date'].max())


    # Group by Id and Date to find the minimum heart rate for each day
    min_hr_chunk = heart_rate_chunk.groupby(['Id', 'Date'])['Value'].min().reset_index()

    # Update the resting_heart_rates dictionary
    for index, row in min_hr_chunk.iterrows():
        user_id = row['Id']
        date = row['Date']
        min_hr = row['Value']
        if (user_id, date) not in resting_heart_rates:
            resting_heart_rates[(user_id, date)] = min_hr
        else:
            resting_heart_rates[(user_id, date)] = min(resting_heart_rates[(user_id, date)], min_hr)

print("Heart rate date range:", min_hr_date, "to", max_hr_date)

# Convert the dictionary to a dataframe
resting_hr_df = pd.DataFrame(resting_heart_rates.items(), columns=['Id_Date', 'RestingHeartRate'])
resting_hr_df[['Id', 'Date']] = pd.DataFrame(resting_hr_df['Id_Date'].tolist(), index=resting_hr_df.index)
resting_hr_df.drop('Id_Date', axis=1, inplace=True)
resting_hr_df['Date'] = pd.to_datetime(resting_hr_df['Date'])


# Merge the resting heart rate data with the main dataframe
merged_data = pd.merge(merged_data, resting_hr_df, left_on=['Id', 'ActivityDate'], right_on=['Id', 'Date'], how='left')
merged_data.drop('Date', axis=1, inplace=True)

# --- k-NN Imputation for RestingHeartRate ---
print("\n--- k-NN Imputation for RestingHeartRate ---")

# Select features for imputation
imputation_features = [
    'TotalMinutesAsleep',
    'VeryActiveMinutes',
    'FairlyActiveMinutes',
    'LightlyActiveMinutes',
    'SedentaryMinutes',
    'RestingHeartRate'
]
imputation_data = merged_data[imputation_features]

# Initialize KNNImputer
imputer = KNNImputer(n_neighbors=5)

# Perform imputation
imputed_data = imputer.fit_transform(imputation_data)

# Update the dataframe with imputed values
imputed_df = pd.DataFrame(imputed_data, columns=imputation_features)
merged_data['RestingHeartRate'] = imputed_df['RestingHeartRate']


# --- Correlation Analysis ---
print("--- Correlation Analysis ---")

# Calculate total active minutes
merged_data['TotalActiveMinutes'] = merged_data['VeryActiveMinutes'] + merged_data['FairlyActiveMinutes'] + merged_data['LightlyActiveMinutes']

# Select the columns for correlation analysis
correlation_data = merged_data[['TotalMinutesAsleep', 'TotalActiveMinutes', 'RestingHeartRate']]

# Calculate the correlation matrix
correlation_matrix = correlation_data.corr()

print("\nCorrelation matrix:")
print(correlation_matrix)

# --- Readiness Score Logic ---
print("\n--- Readiness Score Logic ---")

# Define the weights for each metric
# These weights are just an example and should be adjusted based on the correlation analysis
weight_sleep = 0.4
weight_activity = 0.3
weight_hr = 0.3

# Calculate the readiness score
# This is a simple example, and the logic can be made more complex
merged_data['ReadinessScore'] = (
    (merged_data['TotalMinutesAsleep'] / merged_data['TotalMinutesAsleep'].max()) * weight_sleep +
    (merged_data['TotalActiveMinutes'] / merged_data['TotalActiveMinutes'].max()) * weight_activity +
    (merged_data['RestingHeartRate'].max() - merged_data['RestingHeartRate']) / (merged_data['RestingHeartRate'].max() - merged_data['RestingHeartRate'].min()) * weight_hr
) * 100

# Display the first 5 rows with the readiness score
print("\n--- Merged Data with Readiness Score ---")
print(merged_data[['Id', 'ActivityDate', 'TotalMinutesAsleep', 'TotalActiveMinutes', 'RestingHeartRate', 'ReadinessScore']].head())

# --- NaN Value Analysis ---
print("\n--- NaN Value Analysis ---")
total_rows = len(merged_data)
nan_resting_hr = merged_data['RestingHeartRate'].isna().sum()
nan_readiness_score = merged_data['ReadinessScore'].isna().sum()

print(f"Total rows: {total_rows}")
print(f"Number of NaN in RestingHeartRate: {nan_resting_hr} ({nan_resting_hr/total_rows:.2%})")
print(f"Number of NaN in ReadinessScore: {nan_readiness_score} ({nan_readiness_score/total_rows:.2%})")


# Save the results to a file
with open(results_path, 'w') as f:
    f.write("--- Correlation Matrix ---\n")
    f.write(str(correlation_matrix))
    f.write("\n\n--- Readiness Score Logic ---\n")
    f.write("Readiness Score = ((TotalMinutesAsleep / max_sleep) * 0.4) + ((TotalActiveMinutes / max_active_minutes) * 0.3) + (((max_hr - RestingHeartRate) / (max_hr - min_hr)) * 0.3)) * 100")