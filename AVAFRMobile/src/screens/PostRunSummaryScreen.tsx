import React from 'react';
import { View, Text, Button, StyleSheet, SafeAreaView } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'PostRunSummary'>;

const PostRunSummaryScreen = ({ route, navigation }: Props) => {
  const { duration, distance } = route.params;

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
      </View>

      <View style={styles.buttonContainer}>
        <Button title="Done" onPress={() => navigation.navigate('Home')} />
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
