import React, { useState } from 'react';
import {
  View,
  Text,
  Button,
  StyleSheet,
  SafeAreaView,
  Platform,
  PermissionsAndroid,
  ActivityIndicator,
  ScrollView,
  Alert
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import HealthService from '../services/HealthService';
import apiClient from '../api/client';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

const HomeScreen = ({ navigation }: Props) => {
  const [sleep, setSleep] = useState(0);
  const [steps, setSteps] = useState(0);
  const [heartRate, setHeartRate] = useState(0);
  const [readiness, setReadiness] = useState({
    score: 0,
    message: 'Fetch data to see readiness',
  });
  const [loading, setLoading] = useState(false);

  const handleAuthorization = async () => {
    if (Platform.OS === 'android') {
      try {
        const activityPermission = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACTIVITY_RECOGNITION,
        );
        if (activityPermission !== 'granted') {
          Alert.alert('Permission Denied', 'Activity recognition is required.');
          return;
        }
        
        // Also request Location as it's often needed for Fit to read sensors
        await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        );
      } catch (err) {
        console.warn(err);
      }
    }
    await HealthService.authorize();
  };

  const fetchReadinessData = async () => {
    setLoading(true);
    console.log('Starting fetchReadinessData...');
    try {
      // Execute fetches in parallel for speed
      const [sleepHours, dailySteps, latestHeartRate] = await Promise.all([
        HealthService.getSleepData(),
        HealthService.getDailySteps(),
        HealthService.getHeartRate()
      ]);

      console.log('Data fetched:', { sleepHours, dailySteps, latestHeartRate });

      setSleep(Math.round(sleepHours * 10) / 10);
      setSteps(dailySteps);
      setHeartRate(latestHeartRate);

      // Simple readiness logic
      let score = 0;
      if (sleepHours > 7) score += 40;
      else if (sleepHours > 6) score += 30;

      if (dailySteps < 5000) score += 30; // Resting implies better readiness
      else if (dailySteps < 10000) score += 20;

      if (latestHeartRate > 0 && latestHeartRate < 65) score += 30;
      else if (latestHeartRate < 75) score += 20;

      let message = 'Ready to go!';
      if (score < 50) message = 'Consider a light day';
      else if (score < 75) message = 'Looking good';

      setReadiness({ score, message });

      // Upload to backend
      console.log('Uploading health data...');
      await HealthService.uploadHealthData({
        sleepHours: sleepHours,
        stepCount: dailySteps,
        heartRate: latestHeartRate,
      });
      console.log('Upload complete');

    } catch (error) {
      console.error('Error in fetchReadinessData:', error);
      Alert.alert('Error', 'Failed to fetch or upload data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.headerText}>Pre-Run Readiness</Text>
        </View>

        <View style={styles.dataGrid}>
          <View style={styles.metricBox}>
            <Text style={styles.metricValue}>{sleep} hrs</Text>
            <Text style={styles.metricLabel}>Last Night's Sleep</Text>
          </View>
          <View style={styles.metricBox}>
            <Text style={styles.metricValue}>{steps}</Text>
            <Text style={styles.metricLabel}>Yesterday's Steps</Text>
          </View>
          <View style={styles.metricBox}>
            <Text style={styles.metricValue}>{heartRate} bpm</Text>
            <Text style={styles.metricLabel}>Resting Heart Rate</Text>
          </View>
        </View>

        <View style={styles.readinessContainer}>
          {loading ? (
            <ActivityIndicator size="large" color="#28a745" />
          ) : (
            <>
              <Text style={styles.readinessScore}>{readiness.score}%</Text>
              <Text style={styles.readinessMessage}>{readiness.message}</Text>
            </>
          )}
        </View>

        <View style={styles.buttonContainer}>
          <Button title="1. Authorize Health Data" onPress={handleAuthorization} />
          <View style={styles.spacer} />
          <Button
            title={loading ? "Fetching..." : "2. Fetch Readiness Data"}
            onPress={fetchReadinessData}
            disabled={loading}
          />
          <View style={styles.spacer} />
          <Button
            title="View Run History"
            onPress={() => navigation.navigate('RunHistory')}
            color="#6c757d"
          />
          <View style={styles.spacer} />
          <Button
            title="Start Live Run"
            onPress={() => navigation.navigate('LiveRun')}
            color="#28a745"
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
  },
  scrollContent: {
    flexGrow: 1,
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  headerText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  dataGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 10,
    marginBottom: 20,
  },
  metricBox: {
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    width: '30%',
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 5,
  },
  metricValue: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#007bff',
  },
  metricLabel: {
    fontSize: 12,
    color: '#6c757d',
    marginTop: 5,
  },
  readinessContainer: {
    alignItems: 'center',
    marginVertical: 20,
    padding: 20,
    backgroundColor: 'white',
    marginHorizontal: 20,
    borderRadius: 15,
    elevation: 3,
    minHeight: 150,
    justifyContent: 'center',
  },
  readinessScore: {
    fontSize: 64,
    fontWeight: 'bold',
    color: '#28a745',
  },
  readinessMessage: {
    fontSize: 18,
    color: '#333',
    marginTop: 10,
  },
  buttonContainer: {
    padding: 20,
    marginTop: 'auto',
  },
  spacer: {
    height: 15,
  },
});

export default HomeScreen;
