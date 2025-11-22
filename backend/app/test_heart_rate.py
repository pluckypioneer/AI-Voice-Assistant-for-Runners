import pandas as pd

# Sample merged_data DataFrame
data = {
    'Id': [1, 1, 2, 2],
    'SleepDay': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02'])
}
merged_data = pd.DataFrame(data)

# Sample heart_rate_chunk DataFrame
heart_rate_data = {
    'Id': [1, 1, 1, 1, 2, 2, 2, 2],
    'Time': pd.to_datetime(['2023-01-01 02:00:00', '2023-01-01 03:00:00', '2023-01-02 01:00:00', '2023-01-02 04:00:00',
                           '2023-01-01 02:30:00', '2023-01-01 03:30:00', '2023-01-02 01:30:00', '2023-01-02 04:30:00']),
    'Value': [60, 65, 55, 58, 70, 72, 68, 65]
}
heart_rate_chunk = pd.DataFrame(heart_rate_data)

# --- Resting Heart Rate Calculation ---

# Create a dictionary to store resting heart rate for each user and date
resting_heart_rate = {}

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

# Add the resting heart rate to the merged_data dataframe
merged_data['RestingHeartRate'] = merged_data.apply(
    lambda row: resting_heart_rate.get((row['Id'], row['SleepDay'].date())),
    axis=1
)

# Display the merged_data dataframe with the new column
print(merged_data)
