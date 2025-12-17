#import "RCTHealthModule.h"
#import <React/RCTLog.h>

@implementation RCTHealthModule {
  HKHealthStore *_healthStore;
}

RCT_EXPORT_MODULE(HealthModule);

- (instancetype)init {
  if (self = [super init]) {
    if ([HKHealthStore isHealthDataAvailable]) {
      _healthStore = [[HKHealthStore alloc] init];
    }
  }
  return self;
}

+ (BOOL)requiresMainQueueSetup {
  return NO;
}

- (NSArray<NSString *> *)supportedEvents {
  return @[];
}

RCT_EXPORT_METHOD(authorize:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject) {
  if (![HKHealthStore isHealthDataAvailable]) {
    reject(@"health_kit_unavailable", @"HealthKit is not available", nil);
    return;
  }

  NSSet *readTypes = [NSSet setWithObjects:
                      [HKObjectType quantityTypeForIdentifier:HKQuantityTypeIdentifierStepCount],
                      [HKObjectType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRate],
                      [HKObjectType categoryTypeForIdentifier:HKCategoryTypeIdentifierSleepAnalysis],
                      nil];

  [_healthStore requestAuthorizationToShareTypes:nil readTypes:readTypes completion:^(BOOL success, NSError * _Nullable error) {
    if (!success) {
      reject(@"auth_error", @"Authorization failed", error);
      return;
    }
    resolve(@(success));
  }];
}

RCT_EXPORT_METHOD(getStepCount:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject) {
  HKSampleType *sampleType = [HKSampleType quantityTypeForIdentifier:HKQuantityTypeIdentifierStepCount];
  
  NSCalendar *calendar = [NSCalendar currentCalendar];
  NSDate *now = [NSDate date];
  NSDate *startOfDay = [calendar startOfDayForDate:now];
  
  NSPredicate *predicate = [HKQuery predicateForSamplesWithStartDate:startOfDay endDate:now options:HKQueryOptionStrictStartDate];
  
  HKStatisticsQuery *query = [[HKStatisticsQuery alloc] initWithQuantityType:(HKQuantityType *)sampleType
                                                     quantitySamplePredicate:predicate
                                                                     options:HKStatisticsOptionCumulativeSum
                                                           completionHandler:^(HKStatisticsQuery *query, HKStatistics *result, NSError *error) {
    if (error) {
      reject(@"query_error", @"Error fetching step count", error);
      return;
    }
    
    double steps = 0;
    if (result) {
      steps = [result.sumQuantity doubleValueForUnit:[HKUnit countUnit]];
    }
    resolve(@(steps));
  }];
  
  [_healthStore executeQuery:query];
}

RCT_EXPORT_METHOD(getSleepAnalysis:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject) {
  HKSampleType *sampleType = [HKSampleType categoryTypeForIdentifier:HKCategoryTypeIdentifierSleepAnalysis];
  
  NSCalendar *calendar = [NSCalendar currentCalendar];
  NSDate *now = [NSDate date];
  // Look back 24 hours to find last night's sleep
  NSDate *yesterday = [now dateByAddingTimeInterval:-24*60*60];
  
  NSPredicate *predicate = [HKQuery predicateForSamplesWithStartDate:yesterday endDate:now options:HKQueryOptionStrictStartDate];
  NSSortDescriptor *sortDescriptor = [NSSortDescriptor sortDescriptorWithKey:HKSampleSortIdentifierStartDate ascending:YES];
  
  HKSampleQuery *query = [[HKSampleQuery alloc] initWithSampleType:sampleType
                                                       predicate:predicate
                                                           limit:HKObjectQueryNoLimit
                                                 sortDescriptors:@[sortDescriptor]
                                                  resultsHandler:^(HKSampleQuery *query, NSArray<HKSample *> *results, NSError *error) {
    if (error) {
      reject(@"query_error", @"Error fetching sleep data", error);
      return;
    }
    
    double totalSleepMinutes = 0;
    for (HKCategorySample *sample in results) {
      // value 0: InBed, 1: Asleep, 2: Awake
      // More detailed: 3: Core, 4: Deep, 5: REM
      NSInteger val = sample.value;
      if (val == HKCategoryValueSleepAnalysisAsleep ||
          val == 3 || // Core
          val == 4 || // Deep
          val == 5) { // REM
        NSTimeInterval duration = [sample.endDate timeIntervalSinceDate:sample.startDate];
        totalSleepMinutes += (duration / 60.0);
      }
    }
    
    resolve(@(totalSleepMinutes / 60.0)); // Return hours
  }];
  
  [_healthStore executeQuery:query];
}

RCT_EXPORT_METHOD(getLatestHeartRate:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject) {
  HKSampleType *sampleType = [HKSampleType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRate];
  
  NSSortDescriptor *sortDescriptor = [NSSortDescriptor sortDescriptorWithKey:HKSampleSortIdentifierStartDate ascending:NO];
  
  HKSampleQuery *query = [[HKSampleQuery alloc] initWithSampleType:sampleType
                                                       predicate:nil
                                                           limit:1
                                                 sortDescriptors:@[sortDescriptor]
                                                  resultsHandler:^(HKSampleQuery *query, NSArray<HKSample *> *results, NSError *error) {
    if (error) {
      reject(@"query_error", @"Error fetching heart rate", error);
      return;
    }
    
    double hr = 0;
    if (results.count > 0) {
      HKQuantitySample *sample = (HKQuantitySample *)results.firstObject;
      hr = [sample.quantity doubleValueForUnit:[HKUnit unitFromString:@"count/min"]];
    }
    
    resolve(@(hr));
  }];
  
  [_healthStore executeQuery:query];
}

@end
