import AppleHealthKit, {
  HealthValue,
  HealthKitPermissions,
} from 'react-native-health';

const permissions: HealthKitPermissions = {
  permissions: {
    read: [
      AppleHealthKit.Constants.Permissions.SleepAnalysis,
      AppleHealthKit.Constants.Permissions.Steps,
      AppleHealthKit.Constants.Permissions.HeartRate,
    ],
    write: [],
  },
};

const authorize = (): Promise<boolean> => {
  return new Promise((resolve, reject) => {
    AppleHealthKit.initHealthKit(permissions, (error: string) => {
      if (error) {
        console.log('[ERROR] Cannot grant permissions!', error);
        return reject(false);
      }
      console.log('HealthKit AUTH_SUCCESS');
      resolve(true);
    });
  });
};

const getSleepData = async (): Promise<number> => {
  return new Promise((resolve) => {
    const today = new Date();
    const lastNight = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate() - 1,
      18,
      0,
    ); // 6 PM yesterday
    const options = {
      startDate: lastNight.toISOString(),
      endDate: today.toISOString(),
    };

    AppleHealthKit.getSleepSamples(options, (err: Object, results: HealthValue[]) => {
      if (err) {
        console.log('Error fetching sleep data:', err);
        return resolve(0);
      }
      const totalSleepMinutes = results.reduce((total, session) => {
        if (session.value === 'ASLEEP') {
          const start = new Date(session.startDate);
          const end = new Date(session.endDate);
          return total + (end.getTime() - start.getTime()) / (1000 * 60);
        }
        return total;
      }, 0);
      resolve(totalSleepMinutes / 60);
    });
  });
};

const getDailySteps = async (): Promise<number> => {
  return new Promise((resolve) => {
    const options = {
      date: new Date().toISOString(),
    };
    AppleHealthKit.getStepCount(options, (err: Object, results: HealthValue) => {
      if (err) {
        console.log('Error fetching daily steps:', err);
        return resolve(0);
      }
      resolve(results.value);
    });
  });
};

const getHeartRate = async (): Promise<number> => {
  return new Promise((resolve) => {
    const options = {
      unit: 'bpm',
      startDate: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      ascending: false,
      limit: 1,
    };
    AppleHealthKit.getHeartRateSamples(options, (err: Object, results: HealthValue[]) => {
      if (err) {
        console.log('Error fetching heart rate:', err);
        return resolve(0);
      }
      resolve(results[0]?.value || 0);
    });
  });
};

export default {
  authorize,
  getSleepData,
  getDailySteps,
  getHeartRate,
};
