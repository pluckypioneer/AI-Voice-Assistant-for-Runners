import { Platform } from 'react-native';
import GoogleFitService from './GoogleFitService';
import AppleHealthService from './AppleHealthService';

// This service facade exports the correct health data service based on the platform.
// The UI components will use this service, making them platform-agnostic.

const HealthService = Platform.OS === 'ios' ? AppleHealthService : GoogleFitService;

export default HealthService;
