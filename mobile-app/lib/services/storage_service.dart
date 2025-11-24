import 'package:hive_flutter/hive_flutter.dart';
import 'dart:convert';

class StorageService {
  static const String _userBox = 'user_box';
  static const String _cacheBox = 'cache_box';
  static const String _workoutBox = 'workout_box';
  static const String _membershipBox = 'membership_box';
  static const String _settingsBox = 'settings_box';

  /// Initialize Hive
  static Future<void> initialize() async {
    await Hive.initFlutter();

    // Open boxes
    await Hive.openBox(_userBox);
    await Hive.openBox(_cacheBox);
    await Hive.openBox(_workoutBox);
    await Hive.openBox(_membershipBox);
    await Hive.openBox(_settingsBox);
  }

  /// Get box
  static Box _getBox(String boxName) {
    return Hive.box(boxName);
  }

  // ==================== User Data ====================

  /// Save user data
  static Future<void> saveUser(Map<String, dynamic> userData) async {
    final box = _getBox(_userBox);
    await box.put('current_user', json.encode(userData));
  }

  /// Get user data
  static Map<String, dynamic>? getUser() {
    final box = _getBox(_userBox);
    final userData = box.get('current_user');
    if (userData != null) {
      return json.decode(userData);
    }
    return null;
  }

  /// Clear user data
  static Future<void> clearUser() async {
    final box = _getBox(_userBox);
    await box.delete('current_user');
  }

  // ==================== Cache ====================

  /// Save to cache with expiry
  static Future<void> saveToCache(
    String key,
    dynamic data, {
    Duration? expiry,
  }) async {
    final box = _getBox(_cacheBox);
    final cacheData = {
      'data': data is String ? data : json.encode(data),
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'expiry': expiry?.inMilliseconds,
    };
    await box.put(key, json.encode(cacheData));
  }

  /// Get from cache
  static dynamic getFromCache(String key) {
    final box = _getBox(_cacheBox);
    final cacheData = box.get(key);

    if (cacheData == null) return null;

    try {
      final decoded = json.decode(cacheData);
      final timestamp = decoded['timestamp'] as int;
      final expiry = decoded['expiry'] as int?;

      // Check if expired
      if (expiry != null) {
        final expiryTime = timestamp + expiry;
        if (DateTime.now().millisecondsSinceEpoch > expiryTime) {
          // Cache expired
          box.delete(key);
          return null;
        }
      }

      return decoded['data'];
    } catch (e) {
      print('Error getting from cache: $e');
      return null;
    }
  }

  /// Clear specific cache
  static Future<void> clearCache(String key) async {
    final box = _getBox(_cacheBox);
    await box.delete(key);
  }

  /// Clear all cache
  static Future<void> clearAllCache() async {
    final box = _getBox(_cacheBox);
    await box.clear();
  }

  // ==================== Workouts ====================

  /// Save workout (offline)
  static Future<void> saveWorkout(String workoutId, Map<String, dynamic> workout) async {
    final box = _getBox(_workoutBox);
    await box.put(workoutId, json.encode(workout));
  }

  /// Get workout
  static Map<String, dynamic>? getWorkout(String workoutId) {
    final box = _getBox(_workoutBox);
    final workout = box.get(workoutId);
    if (workout != null) {
      return json.decode(workout);
    }
    return null;
  }

  /// Get all workouts
  static List<Map<String, dynamic>> getAllWorkouts() {
    final box = _getBox(_workoutBox);
    final workouts = <Map<String, dynamic>>[];

    for (var key in box.keys) {
      final workout = box.get(key);
      if (workout != null) {
        workouts.add(json.decode(workout));
      }
    }

    return workouts;
  }

  /// Delete workout
  static Future<void> deleteWorkout(String workoutId) async {
    final box = _getBox(_workoutBox);
    await box.delete(workoutId);
  }

  /// Save pending workout log (for sync when online)
  static Future<void> savePendingWorkoutLog(Map<String, dynamic> workoutLog) async {
    final box = _getBox(_workoutBox);
    final pending = box.get('pending_logs', defaultValue: []) as List;
    pending.add(json.encode(workoutLog));
    await box.put('pending_logs', pending);
  }

  /// Get pending workout logs
  static List<Map<String, dynamic>> getPendingWorkoutLogs() {
    final box = _getBox(_workoutBox);
    final pending = box.get('pending_logs', defaultValue: []) as List;
    return pending.map((log) => json.decode(log) as Map<String, dynamic>).toList();
  }

  /// Clear pending workout logs
  static Future<void> clearPendingWorkoutLogs() async {
    final box = _getBox(_workoutBox);
    await box.delete('pending_logs');
  }

  // ==================== Membership ====================

  /// Save membership data (for offline access)
  static Future<void> saveMembership(Map<String, dynamic> membership) async {
    final box = _getBox(_membershipBox);
    await box.put('current_membership', json.encode(membership));
  }

  /// Get membership data
  static Map<String, dynamic>? getMembership() {
    final box = _getBox(_membershipBox);
    final membership = box.get('current_membership');
    if (membership != null) {
      return json.decode(membership);
    }
    return null;
  }

  /// Save QR code (for offline check-in)
  static Future<void> saveQRCode(String qrCode) async {
    final box = _getBox(_membershipBox);
    await box.put('qr_code', qrCode);
  }

  /// Get QR code
  static String? getQRCode() {
    final box = _getBox(_membershipBox);
    return box.get('qr_code');
  }

  // ==================== Settings ====================

  /// Save setting
  static Future<void> saveSetting(String key, dynamic value) async {
    final box = _getBox(_settingsBox);
    await box.put(key, value);
  }

  /// Get setting
  static dynamic getSetting(String key, {dynamic defaultValue}) {
    final box = _getBox(_settingsBox);
    return box.get(key, defaultValue: defaultValue);
  }

  /// Remove setting
  static Future<void> removeSetting(String key) async {
    final box = _getBox(_settingsBox);
    await box.delete(key);
  }

  /// Clear all settings
  static Future<void> clearAllSettings() async {
    final box = _getBox(_settingsBox);
    await box.clear();
  }

  // ==================== General ====================

  /// Save custom data to specific box
  static Future<void> saveData(String boxName, String key, dynamic data) async {
    try {
      final box = Hive.isBoxOpen(boxName)
          ? Hive.box(boxName)
          : await Hive.openBox(boxName);

      await box.put(key, data is String ? data : json.encode(data));
    } catch (e) {
      print('Error saving data: $e');
    }
  }

  /// Get custom data from specific box
  static dynamic getData(String boxName, String key) {
    try {
      final box = Hive.isBoxOpen(boxName)
          ? Hive.box(boxName)
          : null;

      return box?.get(key);
    } catch (e) {
      print('Error getting data: $e');
      return null;
    }
  }

  /// Clear all data (logout)
  static Future<void> clearAll() async {
    await clearUser();
    await clearAllCache();
    await _getBox(_workoutBox).clear();
    await _getBox(_membershipBox).clear();
    // Don't clear settings box - keep user preferences
  }

  /// Get storage size
  static int getStorageSize() {
    int totalSize = 0;

    final boxes = [_userBox, _cacheBox, _workoutBox, _membershipBox, _settingsBox];
    for (var boxName in boxes) {
      if (Hive.isBoxOpen(boxName)) {
        final box = Hive.box(boxName);
        totalSize += box.length;
      }
    }

    return totalSize;
  }

  /// Compact all boxes (optimize storage)
  static Future<void> compact() async {
    final boxes = [_userBox, _cacheBox, _workoutBox, _membershipBox, _settingsBox];
    for (var boxName in boxes) {
      if (Hive.isBoxOpen(boxName)) {
        await Hive.box(boxName).compact();
      }
    }
  }
}
