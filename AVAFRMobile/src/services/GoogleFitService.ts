import GoogleFit, { BucketUnit, Scopes } from 'react-native-google-fit';

const authorize = async () => {
  const options = {
    scopes: [
      Scopes.FITNESS_ACTIVITY_READ,
      Scopes.FITNESS_SLEEP_READ,
      Scopes.FITNESS_HEART_RATE_READ,
    ],
  };
  try {
    const authResult = await GoogleFit.authorize(options);
    if (authResult.success) {
      console.log('AUTH_SUCCESS');
      return true;
    } else {
      console.log('AUTH_DENIED', authResult.message);
      return false;
    }
  } catch (error) {
    console.log('AUTH_ERROR', error);
    return false;
  }
};

const getSleepData = async () => {
  const today = new Date();
  const lastNight = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1, 18, 0); // 6 PM yesterday
  const options = {
    startDate: lastNight.toISOString(),
    endDate: today.toISOString(),
  };
  try {
    const sleepData = await GoogleFit.getSleepSamples(options);
    // Calculate total sleep in hours
    const totalSleepMinutes = sleepData.reduce((total, session) => {
      if (session.value === 'ASLEEP') {
        const start = new Date(session.startDate);
        const end = new Date(session.endDate);
        return total + (end.getTime() - start.getTime()) / (1000 * 60);
      }
      return total;
    }, 0);
    return totalSleepMinutes / 60;
  } catch (error) {
    console.log('Error fetching sleep data:', error);
    return 0;
  }
};

const getDailySteps = async () => {
  const today = new Date();
  const options = {
    bucketUnit: BucketUnit.DAY,
    bucketInterval: 1,
  };
  try {
    const steps = await GoogleFit.getDailyStepCountSamples(options);
    const todaySteps = steps.find(
      (day) => day.source === 'com.google.android.gms:estimated_steps'
    );
    return todaySteps ? todaySteps.steps[0]?.value || 0 : 0;
  } catch (error) {
    console.log('Error fetching daily steps:', error);
    return 0;
  }
};

const getHeartRate = async () => {
  const today = new Date();
  const last24Hours = new Date(today.getTime() - 24 * 60 * 60 * 1000);
  const options = {
    startDate: last24Hours.toISOString(),
    endDate: today.toISOString(),
  };
  try {
    const heartRateSamples = await GoogleFit.getHeartRateSamples(options);
    // For simplicity, let's find the latest resting heart rate
    const latestSample = heartRateSamples[heartRateSamples.length - 1];
    return latestSample ? latestSample.value : 0;
  } catch (error) {
    console.log('Error fetching heart rate:', error);
    return 0;
  }
};


export default {
  authorize,
  getSleepData,
  getDailySteps,
  getHeartRate,
};
