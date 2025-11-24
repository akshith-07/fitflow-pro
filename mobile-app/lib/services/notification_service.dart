import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'http_client.dart';
import '../constants/api_constants.dart';

class NotificationService {
  final HttpClient _httpClient = HttpClient();
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;

  /// Initialize Firebase Cloud Messaging
  Future<void> initialize() async {
    // Request permission for iOS
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('User granted notification permission');

      // Get FCM token
      final token = await _firebaseMessaging.getToken();
      if (token != null) {
        await saveFCMToken(token);
      }

      // Handle token refresh
      _firebaseMessaging.onTokenRefresh.listen(saveFCMToken);

      // Setup message handlers
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
      FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationClick);
    } else {
      print('User declined or has not accepted notification permission');
    }
  }

  /// Save FCM token to server
  Future<void> saveFCMToken(String token) async {
    try {
      await _httpClient.post(
        '/notifications/register-device',
        data: {
          'fcm_token': token,
          'platform': 'mobile',
        },
      );

      // Save locally
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('fcm_token', token);
    } catch (e) {
      print('Failed to save FCM token: $e');
    }
  }

  /// Handle foreground messages
  void _handleForegroundMessage(RemoteMessage message) {
    print('Got a message whilst in the foreground!');
    print('Message data: ${message.data}');

    if (message.notification != null) {
      print('Message also contained a notification: ${message.notification}');
      // Show local notification using flutter_local_notifications
      // Or handle custom logic based on notification type
    }
  }

  /// Handle notification click
  void _handleNotificationClick(RemoteMessage message) {
    print('A new onMessageOpenedApp event was published!');
    print('Message data: ${message.data}');

    // Navigate based on notification type
    final notificationType = message.data['type'];
    // Implement navigation logic here
  }

  /// Get notification history
  Future<List<Map<String, dynamic>>> getNotifications({
    int? limit,
    int? offset,
    bool? read,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;
      if (read != null) queryParams['read'] = read;

      final response = await _httpClient.get(
        '/notifications',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get notifications';
    }
  }

  /// Mark notification as read
  Future<void> markAsRead(String notificationId) async {
    try {
      await _httpClient.post(
        '/notifications/$notificationId/read',
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to mark notification as read';
    }
  }

  /// Mark all notifications as read
  Future<void> markAllAsRead() async {
    try {
      await _httpClient.post(
        '/notifications/read-all',
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to mark all notifications as read';
    }
  }

  /// Delete notification
  Future<void> deleteNotification(String notificationId) async {
    try {
      await _httpClient.delete(
        ApiConstants.notificationById(notificationId),
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to delete notification';
    }
  }

  /// Get unread notification count
  Future<int> getUnreadCount() async {
    try {
      final response = await _httpClient.get('/notifications/unread-count');
      return response.data['count'] as int;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get unread count';
    }
  }

  /// Update notification preferences
  Future<void> updatePreferences({
    bool? classReminders,
    bool? paymentReminders,
    bool? promotions,
    bool? socialUpdates,
    bool? workoutReminders,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (classReminders != null) data['class_reminders'] = classReminders;
      if (paymentReminders != null) data['payment_reminders'] = paymentReminders;
      if (promotions != null) data['promotions'] = promotions;
      if (socialUpdates != null) data['social_updates'] = socialUpdates;
      if (workoutReminders != null) data['workout_reminders'] = workoutReminders;

      await _httpClient.patch(
        '/notifications/preferences',
        data: data,
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to update preferences';
    }
  }

  /// Get notification preferences
  Future<Map<String, dynamic>> getPreferences() async {
    try {
      final response = await _httpClient.get('/notifications/preferences');
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get preferences';
    }
  }

  /// Test notification
  Future<void> sendTestNotification() async {
    try {
      await _httpClient.post('/notifications/test');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to send test notification';
    }
  }

  /// Unregister device (on logout)
  Future<void> unregisterDevice() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('fcm_token');

      if (token != null) {
        await _httpClient.post(
          '/notifications/unregister-device',
          data: {'fcm_token': token},
        );
      }

      await prefs.remove('fcm_token');
    } catch (e) {
      print('Failed to unregister device: $e');
    }
  }

  /// Schedule local reminder (for offline usage)
  Future<void> scheduleLocalReminder({
    required String title,
    required String body,
    required DateTime scheduledTime,
  }) async {
    // Implement using flutter_local_notifications
    // This is for offline reminders
  }
}
