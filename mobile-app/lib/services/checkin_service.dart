import 'package:dio/dio.dart';
import 'http_client.dart';
import '../constants/api_constants.dart';

class CheckInService {
  final HttpClient _httpClient = HttpClient();

  /// Check in with QR code
  Future<Map<String, dynamic>> checkInWithQR({
    required String qrCode,
    String? locationId,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.checkInQrValidate,
        data: {
          'qr_code': qrCode,
          'location_id': locationId,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Check-in failed';
    }
  }

  /// Check in with biometric
  Future<Map<String, dynamic>> checkInWithBiometric({
    required String biometricData,
    String? locationId,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.checkInBiometric,
        data: {
          'biometric_data': biometricData,
          'location_id': locationId,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Biometric check-in failed';
    }
  }

  /// Check in manually (location-based)
  Future<Map<String, dynamic>> checkIn({
    double? latitude,
    double? longitude,
    String? locationId,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (latitude != null) data['latitude'] = latitude;
      if (longitude != null) data['longitude'] = longitude;
      if (locationId != null) data['location_id'] = locationId;

      final response = await _httpClient.post(
        ApiConstants.checkIns,
        data: data,
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Check-in failed';
    }
  }

  /// Check out
  Future<Map<String, dynamic>> checkOut(String checkInId) async {
    try {
      final response = await _httpClient.post(
        '/check-ins/$checkInId/checkout',
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Check-out failed';
    }
  }

  /// Get check-in history
  Future<List<Map<String, dynamic>>> getCheckInHistory({
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
    int? offset,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;

      final response = await _httpClient.get(
        ApiConstants.checkIns,
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get check-in history';
    }
  }

  /// Get current check-ins (who's in gym now)
  Future<List<Map<String, dynamic>>> getCurrentCheckIns() async {
    try {
      final response = await _httpClient.get(ApiConstants.checkInCurrent);
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get current check-ins';
    }
  }

  /// Get check-in stats
  Future<Map<String, dynamic>> getCheckInStats({
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
        '/check-ins/stats',
        queryParameters: queryParams,
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get check-in stats';
    }
  }

  /// Get member's last check-in
  Future<Map<String, dynamic>?> getLastCheckIn() async {
    try {
      final response = await _httpClient.get('/check-ins/last');
      return response.data;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return null;
      }
      throw e.error ?? 'Failed to get last check-in';
    }
  }

  /// Verify if member is currently checked in
  Future<bool> isCurrentlyCheckedIn() async {
    try {
      final lastCheckIn = await getLastCheckIn();
      if (lastCheckIn == null) return false;

      // Check if check_out_time is null (meaning still checked in)
      return lastCheckIn['check_out_time'] == null;
    } catch (e) {
      return false;
    }
  }

  /// Get check-in streak
  Future<Map<String, dynamic>> getCheckInStreak() async {
    try {
      final response = await _httpClient.get('/check-ins/streak');
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get check-in streak';
    }
  }

  /// Validate check-in eligibility
  Future<Map<String, dynamic>> validateCheckIn() async {
    try {
      final response = await _httpClient.get('/check-ins/validate');
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to validate check-in eligibility';
    }
  }
}
