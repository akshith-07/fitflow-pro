import 'package:dio/dio.dart';
import 'http_client.dart';
import '../constants/api_constants.dart';

class TrainerService {
  final HttpClient _httpClient = HttpClient();

  /// Get all trainers
  Future<List<Map<String, dynamic>>> getTrainers({
    String? specialization,
    int? limit,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (specialization != null) queryParams['specialization'] = specialization;
      if (limit != null) queryParams['limit'] = limit;

      final response = await _httpClient.get(
        ApiConstants.trainers,
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get trainers';
    }
  }

  /// Get trainer by ID
  Future<Map<String, dynamic>> getTrainerById(String trainerId) async {
    try {
      final response = await _httpClient.get(
        ApiConstants.trainerById(trainerId),
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get trainer details';
    }
  }

  /// Get trainer schedule/availability
  Future<List<Map<String, dynamic>>> getTrainerSchedule({
    required String trainerId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }

      final response = await _httpClient.get(
        ApiConstants.trainerSchedule(trainerId),
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get trainer schedule';
    }
  }

  /// Book personal training session
  Future<Map<String, dynamic>> bookSession({
    required String trainerId,
    required DateTime startTime,
    required DateTime endTime,
    String? notes,
  }) async {
    try {
      final response = await _httpClient.post(
        '/trainers/$trainerId/book',
        data: {
          'start_time': startTime.toIso8601String(),
          'end_time': endTime.toIso8601String(),
          'notes': notes,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to book session';
    }
  }

  /// Cancel training session
  Future<void> cancelSession(String sessionId) async {
    try {
      await _httpClient.delete('/trainers/sessions/$sessionId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to cancel session';
    }
  }

  /// Get my training sessions
  Future<List<Map<String, dynamic>>> getMySessions({
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
        '/trainers/my-sessions',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get sessions';
    }
  }

  /// Get upcoming sessions
  Future<List<Map<String, dynamic>>> getUpcomingSessions() async {
    return getMySessions(
      status: 'scheduled',
      startDate: DateTime.now(),
    );
  }

  /// Rate trainer
  Future<void> rateTrainer({
    required String trainerId,
    required int rating,
    String? review,
  }) async {
    try {
      await _httpClient.post(
        '/trainers/$trainerId/rate',
        data: {
          'rating': rating,
          'review': review,
        },
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to rate trainer';
    }
  }

  /// Get trainer reviews
  Future<List<Map<String, dynamic>>> getTrainerReviews(String trainerId) async {
    try {
      final response = await _httpClient.get(
        '/trainers/$trainerId/reviews',
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get reviews';
    }
  }

  /// Get specializations
  Future<List<String>> getSpecializations() async {
    try {
      final response = await _httpClient.get('/trainers/specializations');
      return List<String>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get specializations';
    }
  }

  /// Search trainers
  Future<List<Map<String, dynamic>>> searchTrainers(String query) async {
    try {
      final response = await _httpClient.get(
        '/trainers/search',
        queryParameters: {'q': query},
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to search trainers';
    }
  }

  /// Get recommended trainers
  Future<List<Map<String, dynamic>>> getRecommendedTrainers() async {
    try {
      final response = await _httpClient.get('/trainers/recommended');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get recommended trainers';
    }
  }

  /// Purchase training package
  Future<Map<String, dynamic>> purchasePackage({
    required String trainerId,
    required String packageId,
    String? paymentMethodId,
  }) async {
    try {
      final response = await _httpClient.post(
        '/trainers/$trainerId/purchase-package',
        data: {
          'package_id': packageId,
          'payment_method_id': paymentMethodId,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to purchase package';
    }
  }

  /// Get my training packages
  Future<List<Map<String, dynamic>>> getMyPackages() async {
    try {
      final response = await _httpClient.get('/trainers/my-packages');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get packages';
    }
  }
}
