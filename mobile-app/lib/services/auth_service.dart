import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'http_client.dart';
import '../constants/api_constants.dart';
import '../config/app_config.dart';
import '../models/user.dart';

class AuthService {
  final HttpClient _httpClient = HttpClient();

  /// Register a new user
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String phone,
    required String organizationId,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.register,
        data: {
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
          'phone': phone,
          'organization_id': organizationId,
          'role': 'member',
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Registration failed';
    }
  }

  /// Login with email and password
  Future<User> login({
    required String email,
    required String password,
  }) async {
    try {
      // Prepare form data for OAuth2
      final formData = FormData.fromMap({
        'username': email, // OAuth2 uses 'username' field
        'password': password,
      });

      final response = await _httpClient.post(
        ApiConstants.login,
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        ),
      );

      final data = response.data;

      // Save tokens
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConfig.accessTokenKey, data['access_token']);
      await prefs.setString(AppConfig.refreshTokenKey, data['refresh_token']);

      // Get user data
      final user = await getCurrentUser();

      return user;
    } on DioException catch (e) {
      throw e.error ?? 'Login failed';
    }
  }

  /// Get current logged-in user
  Future<User> getCurrentUser() async {
    try {
      final response = await _httpClient.get('/auth/me');

      final user = User.fromJson(response.data);

      // Cache user data
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConfig.userDataKey, user.toJsonString());

      return user;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get user data';
    }
  }

  /// Get cached user data
  Future<User?> getCachedUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userData = prefs.getString(AppConfig.userDataKey);

      if (userData != null) {
        return User.fromJsonString(userData);
      }

      return null;
    } catch (e) {
      return null;
    }
  }

  /// Refresh access token
  Future<void> refreshToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final refreshToken = prefs.getString(AppConfig.refreshTokenKey);

      if (refreshToken == null) {
        throw 'No refresh token available';
      }

      final response = await _httpClient.post(
        ApiConstants.refresh,
        data: {'refresh_token': refreshToken},
      );

      final data = response.data;

      // Save new tokens
      await prefs.setString(AppConfig.accessTokenKey, data['access_token']);
      await prefs.setString(AppConfig.refreshTokenKey, data['refresh_token']);
    } on DioException catch (e) {
      throw e.error ?? 'Token refresh failed';
    }
  }

  /// Logout user
  Future<void> logout() async {
    try {
      // Call logout endpoint (optional)
      try {
        await _httpClient.post(ApiConstants.logout);
      } catch (e) {
        // Ignore errors from server, proceed with local logout
      }

      // Clear local storage
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(AppConfig.accessTokenKey);
      await prefs.remove(AppConfig.refreshTokenKey);
      await prefs.remove(AppConfig.userDataKey);
    } catch (e) {
      throw 'Logout failed';
    }
  }

  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(AppConfig.accessTokenKey);
      return token != null;
    } catch (e) {
      return false;
    }
  }

  /// Forgot password
  Future<void> forgotPassword(String email) async {
    try {
      await _httpClient.post(
        ApiConstants.forgotPassword,
        data: {'email': email},
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to send reset email';
    }
  }

  /// Reset password
  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    try {
      await _httpClient.post(
        ApiConstants.resetPassword,
        data: {
          'token': token,
          'new_password': newPassword,
        },
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to reset password';
    }
  }

  /// Verify email
  Future<void> verifyEmail(String token) async {
    try {
      await _httpClient.post(
        ApiConstants.verifyEmail,
        data: {'token': token},
      );
    } on DioException catch (e) {
      throw e.error ?? 'Email verification failed';
    }
  }

  /// Enable/disable biometric authentication
  Future<void> setBiometricEnabled(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(AppConfig.biometricEnabledKey, enabled);
  }

  /// Check if biometric is enabled
  Future<bool> isBiometricEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(AppConfig.biometricEnabledKey) ?? false;
  }

  /// Save credentials for biometric login
  Future<void> saveBiometricCredentials({
    required String email,
    required String password,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    // In production, use secure storage like flutter_secure_storage
    await prefs.setString('biometric_email', email);
    await prefs.setString('biometric_password', password);
  }

  /// Get saved biometric credentials
  Future<Map<String, String>?> getBiometricCredentials() async {
    final prefs = await SharedPreferences.getInstance();
    final email = prefs.getString('biometric_email');
    final password = prefs.getString('biometric_password');

    if (email != null && password != null) {
      return {'email': email, 'password': password};
    }

    return null;
  }
}
