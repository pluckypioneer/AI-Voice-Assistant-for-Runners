import GoogleFit, { BucketUnit, Scopes } from 'react-native-google-fit';
import apiClient from '../api/client';

// 定义健康数据类型
interface HealthData {
  sleepHours?: number;
  stepCount?: number;
  heartRate?: number;
}

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
  const startDate = lastNight.toISOString();
  const endDate = today.toISOString();
  try {
    // getSleepSamples 需要两个参数：日期对象和inLocalTimeZone布尔值
    const sleepData = await GoogleFit.getSleepSamples({ startDate, endDate }, true);
    // Calculate total sleep in hours
    const totalSleepMinutes = sleepData.reduce((total, session: any) => {
      // 修复类型访问问题，使用 any 类型来避免类型检查错误
      if (session.value === 'ASLEEP' || session.sleepStage === 4) { // 4 表示深度睡眠
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
    startDate: new Date(today.getFullYear(), today.getMonth(), today.getDate()).toISOString(),
    endDate: today.toISOString(),
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
  const options = {
    startDate: new Date(today.getFullYear(), today.getMonth(), today.getDate()).toISOString(),
    endDate: today.toISOString(),
    bucketUnit: BucketUnit.DAY,
    bucketInterval: 1,
  };
  try {
    const heartRate = await GoogleFit.getHeartRateSamples(options);
    return heartRate[0]?.value || 0;
  } catch (error) {
    console.log('Error fetching heart rate samples:', error);
    return 0;
  }
};

// 上传健康数据到后端
const uploadHealthData = async (data: HealthData): Promise<boolean> => {
  try {
    // 上传睡眠数据
    if (data.sleepHours !== undefined) {
      await apiClient.post('/api/v1/health-data/upload', {
        data_type: 'sleep',
        data: { hours: data.sleepHours },
      });
    }

    // 上传步数数据
    if (data.stepCount !== undefined) {
      await apiClient.post('/api/v1/health-data/upload', {
        data_type: 'steps',
        data: { count: data.stepCount },
      });
    }

    // 上传心率数据
    if (data.heartRate !== undefined) {
      await apiClient.post('/api/v1/health-data/upload', {
        data_type: 'heart_rate',
        data: { value: data.heartRate },
      });
    }

    console.log('Health data uploaded successfully');
    return true;
  } catch (error) {
    console.error('Error uploading health data:', error);
    return false;
  }
};

export default {
  authorize,
  getSleepData,
  getDailySteps,
  getHeartRate,
  uploadHealthData,
};
