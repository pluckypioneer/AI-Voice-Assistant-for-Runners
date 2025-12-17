import React, { useEffect, useState } from 'react';
import { View, Text, Button, StyleSheet, SafeAreaView, Alert, ActivityIndicator, ScrollView } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import apiClient from '../api/client';
import Tts from 'react-native-tts';

type Props = NativeStackScreenProps<RootStackParamList, 'PostRunSummary'>;

const PostRunSummaryScreen = ({ route, navigation }: Props) => {
  const { duration, distance } = route.params;
  const [heartRate, setHeartRate] = useState(0);
  const [stepCount, setStepCount] = useState(0);
  const [insight, setInsight] = useState<string>('');
  const [loadingInsight, setLoadingInsight] = useState(false);
  const [saving, setSaving] = useState(false);

  // Initialize TTS
  useEffect(() => {
    Tts.getInitStatus().then(() => {
      Tts.setDefaultLanguage('en-US');
    }, (err) => {
      if (err.code === 'no_engine') {
        Tts.requestInstallEngine();
      }
    });
  }, []);

  // 模拟获取心率和步数数据
  useEffect(() => {
    // 在实际应用中，这里应该从健康服务获取实时数据
    const hr = Math.floor(Math.random() * 40) + 60; // 模拟心率 60-100 bpm
    const steps = Math.floor(Math.random() * 5000) + 5000; // 模拟步数 5000-10000
    setHeartRate(hr);
    setStepCount(steps);

    // Fetch Insight
    fetchInsight(hr, steps);
  }, []);

  const fetchInsight = async (hr: number, steps: number) => {
    setLoadingInsight(true);
    try {
      const response = await apiClient.post('/api/v1/runs/analyze', {
        distance: parseFloat(distance as unknown as string), // Ensure it's a number
        duration: String(duration),
        heart_rate: hr,
        step_count: steps
      });
      const text = response.data.insight;
      setInsight(text);
      Tts.speak(text);
    } catch (error) {
      console.error('Error fetching insight:', error);
      // Fallback message if API fails
      setInsight('Great run! Keep it up!');
    } finally {
      setLoadingInsight(false);
    }
  };

  const uploadRunData = async () => {
    setSaving(true);
    try {
      // Use the new JSON endpoint for saving runs
      const runData = {
        distance: parseFloat(distance as unknown as string),
        duration: String(duration),
        heart_rate: heartRate,
        step_count: stepCount
      };

      // Upload data to backend
      const response = await apiClient.post('/api/v1/runs/save', runData);

      console.log('Run data saved successfully:', response.data);
      Alert.alert('Success', 'Run saved!', [
        { text: 'OK', onPress: () => navigation.navigate('Home') }
      ]);
    } catch (error) {
      console.error('Error saving run data:', error);
      Alert.alert('Error', 'Failed to save run data.');
      setSaving(false);
    }
  };

  const handleDone = () => {
    uploadRunData();
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.headerText}>Run Summary</Text>
        </View>

        <View style={styles.summaryContainer}>
          <View style={styles.metricBox}>
            <Text style={styles.metricLabel}>Duration</Text>
            <Text style={styles.metricValue}>{duration}</Text>
          </View>
          <View style={styles.metricBox}>
            <Text style={styles.metricLabel}>Distance</Text>
            <Text style={styles.metricValue}>{distance} km</Text>
          </View>
          <View style={styles.metricBox}>
            <Text style={styles.metricLabel}>Average Heart Rate</Text>
            <Text style={styles.metricValue}>{heartRate} bpm</Text>
          </View>
          <View style={styles.metricBox}>
            <Text style={styles.metricLabel}>Step Count</Text>
            <Text style={styles.metricValue}>{stepCount}</Text>
          </View>
        </View>

        <View style={styles.insightContainer}>
          <Text style={styles.insightTitle}>AI Analysis</Text>
          {loadingInsight ? (
            <ActivityIndicator size="small" color="#007bff" />
          ) : (
            <Text style={styles.insightText}>{insight}</Text>
          )}
        </View>

        <View style={styles.buttonContainer}>
          <Button title={saving ? "Saving..." : "Save & Done"} onPress={handleDone} disabled={saving} />
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
    paddingBottom: 40,
  },
  header: {
    padding: 20,
    alignItems: 'center',
    marginTop: 20,
  },
  headerText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  summaryContainer: {
    alignItems: 'center',
  },
  metricBox: {
    alignItems: 'center',
    marginVertical: 15,
  },
  metricLabel: {
    fontSize: 18,
    color: '#6c757d',
  },
  metricValue: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#007bff',
    marginTop: 5,
  },
  insightContainer: {
    margin: 20,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
  },
  insightTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  insightText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#555',
  },
  buttonContainer: {
    padding: 20,
  },
});

export default PostRunSummaryScreen;
