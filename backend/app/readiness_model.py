import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_readiness_score(df):
    """
    Calculates the readiness score for each row in the DataFrame.
    """
    # Define the weights for each metric
    weight_sleep = 0.4
    weight_activity = 0.3
    weight_hr = 0.3

    # Calculate total active minutes
    df['TotalActiveMinutes'] = df['VeryActiveMinutes'] + df['FairlyActiveMinutes'] + df['LightlyActiveMinutes']

    # Calculate the readiness score
    df['ReadinessScore'] = (
        (df['TotalMinutesAsleep'] / df['TotalMinutesAsleep'].max()) * weight_sleep +
        (df['TotalActiveMinutes'] / df['TotalActiveMinutes'].max()) * weight_activity +
        (df['RestingHeartRate'].max() - df['RestingHeartRate']) / (df['RestingHeartRate'].max() - df['RestingHeartRate'].min()) * weight_hr
    ) * 100

    return df

def get_workout_recommendation(score):
    """
    Provides a workout recommendation based on the readiness score.
    """
    if score >= 80:
        return "You're in peak condition! Go for a high-intensity workout."
    elif score >= 60:
        return "Feeling good! A moderate workout would be great today."
    elif score >= 40:
        return "Take it easy. A light workout or a walk is a good choice."
    else:
        return "Your body needs rest. Consider a recovery day."

def main():
    """
    Main function to demonstrate the readiness score model and workout recommendations.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        synthetic_data_path = os.path.join(script_dir, 'synthetic_data.csv')

        logging.info(f"Loading synthetic data from {synthetic_data_path}...")
        df = pd.read_csv(synthetic_data_path)
        logging.info("Synthetic data loaded successfully.")

        logging.info("Calculating readiness scores...")
        df_with_scores = calculate_readiness_score(df)
        logging.info("Readiness scores calculated.")

        # Get a recommendation for the first user
        first_user_score = df_with_scores.iloc[0]['ReadinessScore']
        recommendation = get_workout_recommendation(first_user_score)

        logging.info(f"\n--- Example Recommendation ---")
        logging.info(f"Readiness Score for first user: {first_user_score:.2f}")
        logging.info(f"Workout Recommendation: {recommendation}")

        # Save the data with readiness scores to a new CSV
        output_path = os.path.join(script_dir, 'synthetic_data_with_readiness.csv')
        df_with_scores.to_csv(output_path, index=False)
        logging.info(f"Data with readiness scores saved to {output_path}")

    except FileNotFoundError as e:
        logging.error(f"Error: {e}. Make sure 'synthetic_data.csv' exists.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
