import { NativeModules } from 'react-native';
import apiClient from '../api/client';

const { HealthModule } = NativeModules;

// 定义健康数据类型
interface HealthData {
  sleepHours?: number;
  stepCount?: number;
  heartRate?: number;
}

const authorize = async (): Promise<boolean> => {
  try {
    const result = await HealthModule.authorize();
    console.log('HealthKit authorization result:', result);
    return result;
  } catch (error) {
    console.log('Error authorizing HealthKit:', error);
    return false;
  }
};

const getSleepData = async (): Promise<number> => {
  try {
    const sleepHours = await HealthModule.getSleepAnalysis();
    return sleepHours;
  } catch (error) {
    console.log('Error fetching sleep data:', error);
    return 0;
  }
};

const getDailySteps = async (): Promise<number> => {
  try {
    const steps = await HealthModule.getStepCount();
    return Math.round(steps);
  } catch (error) {
    console.log('Error fetching daily steps:', error);
    return 0;
  }
};

const getHeartRate = async (): Promise<number> => {
  try {
    const heartRate = await HealthModule.getLatestHeartRate();
    return heartRate;
  } catch (error) {
    console.log('Error fetching heart rate:', error);
    return 0;
  }
};

// Upload health data to backend
const uploadHealthData = async (data: HealthData): Promise<boolean> => {
  try {
    await apiClient.post('/api/v1/health-data/save', {
      sleep_hours: data.sleepHours,
      step_count: data.stepCount,
      heart_rate: data.heartRate,
      timestamp: new Date().toISOString()
    });

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


