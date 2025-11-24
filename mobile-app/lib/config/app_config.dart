class AppConfig {
  // API Configuration
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  static const String apiVersion = 'v1';
  static const String apiPrefix = '/api/$apiVersion';

  // App Information
  static const String appName = 'FitFlow Pro';
  static const String appVersion = '1.0.0';
  static const String appBuildNumber = '1';

  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userDataKey = 'user_data';
  static const String themeKey = 'theme_mode';
  static const String biometricEnabledKey = 'biometric_enabled';
  static const String onboardingCompleteKey = 'onboarding_complete';

  // API Timeouts (in seconds)
  static const int connectionTimeout = 30;
  static const int receiveTimeout = 30;
  static const int sendTimeout = 30;

  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // Cache Duration (in minutes)
  static const int profileCacheDuration = 5;
  static const int classesCacheDuration = 10;
  static const int scheduleCacheDuration = 60;

  // Feature Flags
  static const bool enableBiometric = true;
  static const bool enablePushNotifications = true;
  static const bool enableOfflineMode = true;
  static const bool enableAnalytics = true;

  // Social Login
  static const bool enableGoogleLogin = true;
  static const bool enableAppleLogin = true;
  static const bool enableFacebookLogin = false;

  // Debug
  static const bool isDebugMode = bool.fromEnvironment('DEBUG', defaultValue: false);
  static const bool enableNetworkLogging = true;
}
