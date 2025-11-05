# AI Voice Assistant for Runners (Mobile App)

## Overview

This is the frontend mobile application for the AI Voice Assistant for Runners. It is built with React Native and is cross-platform, supporting both Android (via Google Fit) and iOS (via Apple HealthKit).

## Features

- **Pre-Run Readiness Score**: Before a run, the app fetches your recent health data (sleep, steps, resting heart rate) to calculate a "Readiness Score," helping you decide on the intensity of your workout.
- **Live Run Simulation**: A simulated in-run experience showing key metrics like time, distance, and heart rate in real-time.
- **In-Run Alerts**: The live run screen provides alerts based on simulated data (e.g., "Heart rate is high! Slow down.").
- **Post-Run Summary**: A summary screen displaying the results of your completed run.

---

## Environment Setup

Before you can run the project, you must set up your development environment for React Native. Follow the instructions for your specific operating system.

### ➤ Windows

We recommend using the [Chocolatey](https://chocolatey.org/) package manager for Windows.

1.  **Install Dependencies**: Open PowerShell as Administrator and run:
    ```powershell
    choco install -y nodejs-lts watchman openjdk --version=17
    ```
2.  **Install Android Studio**: Download and install [Android Studio](https://developer.android.com/studio) for Windows. In the setup wizard, make sure to install:
    - Android SDK
    - Android SDK Platform
    - Android Virtual Device
3.  **Configure Environment Variables**: 
    - Open the "Edit the system environment variables" control panel.
    - Add a new `JAVA_HOME` variable pointing to your JDK 17 installation directory.
    - Add a new `ANDROID_HOME` variable pointing to the Android SDK location (usually `C:\Users\YOUR_USERNAME\AppData\Local\Android\Sdk`).
    - Add the Android platform-tools to your `Path` variable (e.g., `%ANDROID_HOME%\platform-tools`).

### ➤ macOS

We recommend using the [Homebrew](https://brew.sh/) package manager for macOS.

1.  **Install Dependencies**: Open your terminal and run:
    ```bash
    brew install node watchman openjdk@17
    ```
2.  **Install Xcode**: Install Xcode from the Mac App Store. This will also install the iOS Simulator and required command-line tools.
3.  **Install CocoaPods**: 
    ```bash
    sudo gem install cocoapods
    ```
4.  **Install Android Studio**: Download and install [Android Studio](https://developer.android.com/studio) for Mac.
5.  **Configure Environment Variables**: Add the following lines to your `~/.zshrc` file:
    ```bash
    export ANDROID_HOME=$HOME/Library/Android/sdk
    export PATH=$PATH:$ANDROID_HOME/emulator
    export PATH=$PATH:$ANDROID_HOME/platform-tools
    export JAVA_HOME=$(/usr/libexec/java_home -v 17)
    ```
    Then, reload your shell: `source ~/.zshrc`

### ➤ Linux (Debian/Ubuntu)

1.  **Install Dependencies**: Open your terminal and run:
    ```bash
    sudo apt-get update && sudo apt-get install -y nodejs npm watchman openjdk-17-jdk
    ```
2.  **Install Android Studio**: Download and install [Android Studio](https://developer.android.com/studio) for Linux.
3.  **Configure Environment Variables**: Add the following lines to your `~/.bashrc` or `~/.zshrc` file:
    ```bash
    export ANDROID_HOME=$HOME/Android/Sdk
    export PATH=$PATH:$ANDROID_HOME/emulator
    export PATH=$PATH:$ANDROID_HOME/platform-tools
    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 # Verify this path
    ```
    Then, reload your shell (e.g., `source ~/.bashrc`).

---

## ✍️ Configuration

To use the health data features, you must configure the app with the appropriate service credentials.

### Android (Google Fit)

1.  **Open the Google Cloud Console**: Navigate to [console.cloud.google.com](https://console.cloud.google.com/).
2.  **Create a Project**: Set up a new project.
3.  **Enable the Fitness API**: In "APIs & Services" > "Library", search for and enable the "Fitness API".
4.  **Configure OAuth Consent Screen**: Set this up under "APIs & Services". You will need to add your email as a test user during development.
5.  **Create an OAuth 2.0 Client ID**:
    - Go to "Credentials", click "Create Credentials" > "OAuth client ID".
    - Select **Android** as the application type.
    - **Package name**: `com.avafrmobile`
    - **SHA-1 certificate fingerprint**: Get this by running the following command in the `AVAFRMobile/android` directory:
      ```bash
      ./gradlew signingReport
      ```
      Copy the SHA-1 value from the `debug` variant.
6.  Create the credential. No file download is necessary.

### iOS (Apple HealthKit)

The project is already pre-configured.

1.  **Info.plist**: The necessary privacy descriptions are already included.
2.  **Xcode Capabilities**: After running `pod install`, open the generated `.xcworkspace` file in Xcode. You must then enable the **HealthKit** capability in the "Signing & Capabilities" tab for the `AVAFRMobile` target.

---

## 🚀 Running the Application

1.  **Install Dependencies**: From the `AVAFRMobile` root directory, run:
    ```bash
    npm install
    ```

### Android

It is recommended to use two separate terminals for a smoother experience.

1.  **Terminal 1 (Start Metro)**:
    ```bash
    npx react-native start
    ```
2.  **Terminal 2 (Run the App)**:
    Make sure your Android emulator is running or a device is connected.
    ```bash
    npx react-native run-android
    ```

### iOS (Requires macOS)

1.  **Install iOS Dependencies**:
    ```bash
    cd ios
    pod install
    cd ..
    ```
2.  **Run the App**:
    Make sure your iOS Simulator is running.
    ```bash
    npx react-native run-ios
    ```

---

## 📱 How to Use the App

1.  Launch the application.
2.  On the Home Screen, tap **"1. Authorize..."**. This will trigger the native sign-in and permission prompt for either Google Fit or Apple Health.
3.  Once authorized, tap **"2. Fetch Readiness Data"** to see your latest health metrics and readiness score.
4.  Tap **"Start Live Run"** to go to the simulated in-run dashboard.
5.  On the Live Run screen, you can **Pause/Resume** the run or **End Run** to see the summary.
