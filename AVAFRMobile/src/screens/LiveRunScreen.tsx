import React, { useState, useEffect, useRef } from 'react';
import { View, Text, Button, StyleSheet, SafeAreaView } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'LiveRun'>;

const LiveRunScreen = ({ navigation }: Props) => {
  const [isActive, setIsActive] = useState(true);
  const [seconds, setSeconds] = useState(0);
  const [distance, setDistance] = useState(0);
  const [heartRate, setHeartRate] = useState(120);
  const [alert, setAlert] = useState('Keep a steady pace!');

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isActive) {
      intervalRef.current = setInterval(() => {
        setSeconds((s) => s + 1);
        // Simulate distance (e.g., 4.5 m/s)
        setDistance((d) => d + 0.0045);

        // Simulate heart rate fluctuations
        setHeartRate((hr) => {
          const newHr = hr + (Math.random() - 0.5) * 4;
          return Math.max(100, Math.min(180, newHr)); // Clamp between 100 and 180
        });

        // Alerting logic
        if (heartRate > 165) {
          setAlert('Heart rate is high! Slow down.');
        } else if (heartRate < 120) {
          setAlert('Push a little harder!');
        } else {
          setAlert('Looking good!');
        }
      }, 1000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isActive, heartRate]);

  const formatTime = () => {
    const getSeconds = `0${seconds % 60}`.slice(-2);
    const minutes = Math.floor(seconds / 60);
    const getMinutes = `0${minutes % 60}`.slice(-2);
    const getHours = `0${Math.floor(seconds / 3600)}`.slice(-2);
    return `${getHours}:${getMinutes}:${getSeconds}`;
  };

  const handleEndRun = () => {
    setIsActive(false);
    navigation.replace('PostRunSummary', {
      duration: formatTime(),
      distance: parseFloat(distance.toFixed(2)),
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.alertContainer}>
        <Text style={styles.alertText}>{alert}</Text>
      </View>

      <View style={styles.mainMetricsContainer}>
        <Text style={styles.distanceText}>{distance.toFixed(2)}</Text>
        <Text style={styles.distanceLabel}>km</Text>
      </View>

      <View style={styles.secondaryMetricsContainer}>
        <View style={styles.metricBox}>
          <Text style={styles.metricLabel}>Time</Text>
          <Text style={styles.metricValue}>{formatTime()}</Text>
        </View>
        <View style={styles.metricBox}>
          <Text style={styles.metricLabel}>Heart Rate</Text>
          <Text style={styles.metricValue}>{heartRate} bpm</Text>
        </View>
      </View>

      <View style={styles.buttonContainer}>
        <Button
          title={isActive ? 'Pause' : 'Resume'}
          onPress={() => setIsActive(!isActive)}
        />
        <View style={styles.spacer} />
        <Button title="End Run" onPress={handleEndRun} color="#dc3545" />
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'space-between',
  },
  alertContainer: {
    backgroundColor: '#ffc107',
    padding: 15,
    alignItems: 'center',
  },
  alertText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  mainMetricsContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  distanceText: {
    fontSize: 100,
    color: '#fff',
    fontWeight: 'bold',
  },
  distanceLabel: {
    fontSize: 24,
    color: '#fff',
    marginTop: -10,
  },
  secondaryMetricsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  metricBox: {
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 18,
    color: '#aaa',
  },
  metricValue: {
    fontSize: 36,
    color: '#fff',
    fontWeight: 'bold',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    padding: 30,
  },
  spacer: {
    width: 40,
  },
});

export default LiveRunScreen;
