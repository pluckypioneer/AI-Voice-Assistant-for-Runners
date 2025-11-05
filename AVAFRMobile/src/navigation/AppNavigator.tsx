import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from '../screens/HomeScreen';
import LiveRunScreen from '../screens/LiveRunScreen';
import PostRunSummaryScreen from '../screens/PostRunSummaryScreen';
import { RootStackParamList } from './types';

const Stack = createNativeStackNavigator<RootStackParamList>();

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="LiveRun" component={LiveRunScreen} />
        <Stack.Screen name="PostRunSummary" component={PostRunSummaryScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;