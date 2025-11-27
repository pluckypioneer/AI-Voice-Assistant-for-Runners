import React, { useEffect, useState } from 'react';
import { View, Text, Button, StyleSheet, SafeAreaView, Alert } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import apiClient from '../api/client';

type Props = NativeStackScreenProps<RootStackParamList, 'PostRunSummary'>;

const PostRunSummaryScreen = ({ route, navigation }: Props) => {
  const { duration, distance } = route.params;
  const [heartRate, setHeartRate] = useState(0);
  const [stepCount, setStepCount] = useState(0);

  // 模拟获取心率和步数数据
  useEffect(() => {
    // 在实际应用中，这里应该从健康服务获取实时数据
    setHeartRate(Math.floor(Math.random() * 40) + 60); // 模拟心率 60-100 bpm
    setStepCount(Math.floor(Math.random() * 5000) + 5000); // 模拟步数 5000-10000
  }, []);

  const uploadRunData = async () => {
    try {
      // 创建一个包含跑步数据的JSON对象
      const runData = {
        duration: duration,
        distance: distance,
        heartRate: heartRate,
        stepCount: stepCount,
        timestamp: new Date().toISOString()
      };

      // 将数据转换为Blob
      const jsonData = JSON.stringify(runData);
      // 修复Blob构造函数错误 - 添加lastModified属性
      const blob = new Blob([jsonData], { 
        type: 'application/json',
        lastModified: Date.now()
      } as any);
      // 在React Native中使用Blob创建文件对象
      const file = new File([blob], 'run_data.json', { 
        type: 'application/json',
        lastModified: Date.now()
      } as any);

      // 创建FormData对象
      const formData = new FormData();
      formData.append('file', file);

      // 上传数据到后端
      const response = await apiClient.post('/api/v1/health-data/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Run data uploaded successfully:', response.data);
      Alert.alert('Success', 'Run data uploaded successfully!');
    } catch (error) {
      console.error('Error uploading run data:', error);
      Alert.alert('Error', 'Failed to upload run data.');
    }
  };

  const handleDone = () => {
    uploadRunData();
    navigation.navigate('Home');
  };

  return (
    <SafeAreaView style={styles.container}>
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

      <View style={styles.buttonContainer}>
        <Button title="Done" onPress={handleDone} />
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
    justifyContent: 'space-between',
  },
  header: {
    padding: 20,
    alignItems: 'center',
    marginTop: 40,
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
    marginVertical: 20,
  },
  metricLabel: {
    fontSize: 18,
    color: '#6c757d',
  },
  metricValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#007bff',
    marginTop: 5,
  },
  buttonContainer: {
    padding: 20,
    marginBottom: 40,
  },
});

export default PostRunSummaryScreen;
