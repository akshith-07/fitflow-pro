import 'package:dio/dio.dart';
import 'http_client.dart';
import '../constants/api_constants.dart';
import '../models/class.dart';

class ClassService {
  final HttpClient _httpClient = HttpClient();

  /// Get all classes
  Future<List<GymClass>> getClasses({
    String? category,
    String? instructorId,
    String? difficulty,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (category != null) queryParams['category'] = category;
      if (instructorId != null) queryParams['instructor_id'] = instructorId;
      if (difficulty != null) queryParams['difficulty'] = difficulty;

      final response = await _httpClient.get(
        ApiConstants.classes,
        queryParameters: queryParams,
      );

      return (response.data as List)
          .map((json) => GymClass.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get classes';
    }
  }

  /// Get class by ID
  Future<GymClass> getClassById(String classId) async {
    try {
      final response = await _httpClient.get(ApiConstants.classById(classId));
      return GymClass.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get class details';
    }
  }

  /// Get class schedule
  Future<List<Map<String, dynamic>>> getSchedule({
    DateTime? startDate,
    DateTime? endDate,
    String? classId,
    String? instructorId,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }
      if (classId != null) queryParams['class_id'] = classId;
      if (instructorId != null) queryParams['instructor_id'] = instructorId;

      final response = await _httpClient.get(
        ApiConstants.classSchedule,
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get class schedule';
    }
  }

  /// Get today's schedule
  Future<List<Map<String, dynamic>>> getTodaySchedule() async {
    final now = DateTime.now();
    final startOfDay = DateTime(now.year, now.month, now.day);
    final endOfDay = startOfDay.add(const Duration(days: 1));

    return getSchedule(
      startDate: startOfDay,
      endDate: endOfDay,
    );
  }

  /// Get week schedule
  Future<List<Map<String, dynamic>>> getWeekSchedule({DateTime? startOfWeek}) async {
    final start = startOfWeek ??
        DateTime.now().subtract(Duration(days: DateTime.now().weekday - 1));
    final startOfWeekDate = DateTime(start.year, start.month, start.day);
    final endOfWeek = startOfWeekDate.add(const Duration(days: 7));

    return getSchedule(
      startDate: startOfWeekDate,
      endDate: endOfWeek,
    );
  }

  /// Book a class
  Future<Map<String, dynamic>> bookClass(String scheduleId) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.classBook(scheduleId),
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to book class';
    }
  }

  /// Cancel class booking
  Future<void> cancelBooking(String scheduleId) async {
    try {
      await _httpClient.delete(
        ApiConstants.classCancelBooking(scheduleId),
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to cancel booking';
    }
  }

  /// Get my bookings
  Future<List<Map<String, dynamic>>> getMyBookings({
    String? status,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) queryParams['status'] = status;
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }

      final response = await _httpClient.get(
        '/classes/my-bookings',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get bookings';
    }
  }

  /// Get upcoming bookings
  Future<List<Map<String, dynamic>>> getUpcomingBookings() async {
    return getMyBookings(
      status: 'booked',
      startDate: DateTime.now(),
    );
  }

  /// Get past bookings
  Future<List<Map<String, dynamic>>> getPastBookings({int? limit}) async {
    try {
      final queryParams = <String, dynamic>{
        'status': 'attended',
        'end_date': DateTime.now().toIso8601String(),
      };
      if (limit != null) queryParams['limit'] = limit;

      final response = await _httpClient.get(
        '/classes/my-bookings',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get past bookings';
    }
  }

  /// Join waitlist
  Future<Map<String, dynamic>> joinWaitlist(String scheduleId) async {
    try {
      final response = await _httpClient.post(
        '/classes/$scheduleId/waitlist',
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to join waitlist';
    }
  }

  /// Leave waitlist
  Future<void> leaveWaitlist(String scheduleId) async {
    try {
      await _httpClient.delete(
        '/classes/$scheduleId/waitlist',
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to leave waitlist';
    }
  }

  /// Get waitlist position
  Future<Map<String, dynamic>> getWaitlistPosition(String scheduleId) async {
    try {
      final response = await _httpClient.get(
        ApiConstants.classWaitlist(scheduleId),
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get waitlist position';
    }
  }

  /// Rate a class
  Future<void> rateClass({
    required String scheduleId,
    required int rating,
    String? review,
  }) async {
    try {
      await _httpClient.post(
        '/classes/$scheduleId/rate',
        data: {
          'rating': rating,
          'review': review,
        },
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to rate class';
    }
  }

  /// Get class reviews
  Future<List<Map<String, dynamic>>> getClassReviews(String classId) async {
    try {
      final response = await _httpClient.get(
        '/classes/$classId/reviews',
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get reviews';
    }
  }

  /// Get class categories
  Future<List<String>> getCategories() async {
    try {
      final response = await _httpClient.get('/classes/categories');
      return List<String>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get categories';
    }
  }

  /// Search classes
  Future<List<GymClass>> searchClasses(String query) async {
    try {
      final response = await _httpClient.get(
        '/classes/search',
        queryParameters: {'q': query},
      );

      return (response.data as List)
          .map((json) => GymClass.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw e.error ?? 'Failed to search classes';
    }
  }

  /// Check if class is bookable
  Future<Map<String, dynamic>> checkBookingEligibility(String scheduleId) async {
    try {
      final response = await _httpClient.get(
        '/classes/$scheduleId/check-eligibility',
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to check booking eligibility';
    }
  }
}
