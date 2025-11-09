import pandas as pd

# Load the datasets
daily_activity = pd.read_csv('/home/kita/Downloads/AI-Voice-Assistant-for-Runners/dataset/mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16/dailyActivity_merged.csv')
sleep_day = pd.read_csv('/home/kita/Downloads/AI-Voice-Assistant-for-Runners/dataset/mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16/sleepDay_merged.csv')

# Clean up the column names
daily_activity.columns = daily_activity.columns.str.strip()
sleep_day.columns = sleep_day.columns.str.strip()

# Convert date columns to datetime objects
daily_activity['ActivityDate'] = pd.to_datetime(daily_activity['ActivityDate'], format='%m/%d/%Y')
sleep_day['SleepDay'] = pd.to_datetime(sleep_day['SleepDay'], format='%m/%d/%Y %I:%M:%S %p').dt.date
sleep_day['SleepDay'] = pd.to_datetime(sleep_day['SleepDay'])


# Merge the two dataframes
merged_data = pd.merge(daily_activity, sleep_day, left_on=['Id', 'ActivityDate'], right_on=['Id', 'SleepDay'])

# --- Data Cleaning ---
# Remove duplicates
merged_data.drop_duplicates(inplace=True)



# --- Resting Heart Rate Calculation ---

# Create a dictionary to store resting heart rate for each user and date
resting_heart_rate = {}

# Process heart rate data in chunks
heart_rate_chunk_size = 100000
heart_rate_reader = pd.read_csv('/home/kita/Downloads/AI-Voice-Assistant-for-Runners/dataset/mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16/heartrate_seconds_merged.csv', chunksize=heart_rate_chunk_size)

for i, heart_rate_chunk in enumerate(heart_rate_reader):
    print(f"Processing heart rate chunk {i}...")
    try:
        # Convert 'Time' column to datetime objects
        heart_rate_chunk['Time'] = pd.to_datetime(heart_rate_chunk['Time'], format='%m/%d/%Y %I:%M:%S %p')

        # Iterate through each row in the merged_data to find sleep periods
        for index, row in merged_data.iterrows():
            user_id = row['Id']
            sleep_date = row['SleepDay'].date()

            # Define the sleep period (from midnight to midnight)
            sleep_start = pd.to_datetime(sleep_date)
            sleep_end = sleep_start + pd.Timedelta(days=1)

            # Filter heart rate data for the current user and sleep period
            user_heart_rate = heart_rate_chunk[
                (heart_rate_chunk['Id'] == user_id) &
                (heart_rate_chunk['Time'] >= sleep_start) &
                (heart_rate_chunk['Time'] < sleep_end)
            ]

            # If there is heart rate data for the sleep period, find the minimum
            if not user_heart_rate.empty:
                min_heart_rate = user_heart_rate['Value'].min()

                # Update the resting_heart_rate dictionary
                if (user_id, sleep_date) not in resting_heart_rate:
                    resting_heart_rate[(user_id, sleep_date)] = min_heart_rate
                else:
                    resting_heart_rate[(user_id, sleep_date)] = min(resting_heart_rate[(user_id, sleep_date)], min_heart_rate)
    except Exception as e:
        print(f"Error processing chunk {i}: {e}")

# Add the resting heart rate to the merged_data dataframe
merged_data['RestingHeartRate'] = merged_data.apply(
    lambda row: resting_heart_rate.get((row['Id'], row['SleepDay'].date())),
    axis=1
)

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

# Save the results to a file
with open('/home/kita/Downloads/AI-Voice-Assistant-for-Runners/backend/app/readiness_score_results.txt', 'w') as f:
    f.write("--- Correlation Matrix ---\n")
    f.write(str(correlation_matrix))
    f.write("\n\n--- Readiness Score Logic ---\n")
    f.write("Readiness Score = ((TotalMinutesAsleep / max_sleep) * 0.4) + ((TotalActiveMinutes / max_active_minutes) * 0.3) + (((max_hr - RestingHeartRate) / (max_hr - min_hr)) * 0.3)) * 100")
