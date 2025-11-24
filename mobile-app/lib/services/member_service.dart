import 'package:dio/dio.dart';
import 'http_client.dart';
import '../constants/api_constants.dart';
import '../models/member.dart';

class MemberService {
  final HttpClient _httpClient = HttpClient();

  /// Get current member profile
  Future<Member> getProfile() async {
    try {
      final response = await _httpClient.get('/members/me');
      return Member.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get profile';
    }
  }

  /// Update member profile
  Future<Member> updateProfile({
    required String id,
    String? firstName,
    String? lastName,
    String? phone,
    String? dateOfBirth,
    String? gender,
    Map<String, dynamic>? address,
    String? emergencyContactName,
    String? emergencyContactPhone,
    String? medicalNotes,
    List<String>? fitnessGoals,
    List<String>? tags,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (firstName != null) data['first_name'] = firstName;
      if (lastName != null) data['last_name'] = lastName;
      if (phone != null) data['phone'] = phone;
      if (dateOfBirth != null) data['date_of_birth'] = dateOfBirth;
      if (gender != null) data['gender'] = gender;
      if (address != null) data['address'] = address;
      if (emergencyContactName != null) data['emergency_contact_name'] = emergencyContactName;
      if (emergencyContactPhone != null) data['emergency_contact_phone'] = emergencyContactPhone;
      if (medicalNotes != null) data['medical_notes'] = medicalNotes;
      if (fitnessGoals != null) data['fitness_goals'] = fitnessGoals;
      if (tags != null) data['tags'] = tags;

      final response = await _httpClient.put(
        ApiConstants.memberById(id),
        data: data,
      );

      return Member.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to update profile';
    }
  }

  /// Upload profile photo
  Future<String> uploadProfilePhoto(String filePath) async {
    try {
      final response = await _httpClient.uploadFile(
        '/members/upload-photo',
        filePath,
      );

      return response.data['photo_url'];
    } on DioException catch (e) {
      throw e.error ?? 'Failed to upload photo';
    }
  }

  /// Get member attendance history
  Future<List<Map<String, dynamic>>> getAttendance({
    required String memberId,
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();
      if (limit != null) queryParams['limit'] = limit;

      final response = await _httpClient.get(
        ApiConstants.memberAttendance(memberId),
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get attendance';
    }
  }

  /// Get member payments history
  Future<List<Map<String, dynamic>>> getPayments({
    required String memberId,
    int? limit,
    int? offset,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;

      final response = await _httpClient.get(
        ApiConstants.memberPayments(memberId),
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get payments';
    }
  }

  /// Get member bookings
  Future<List<Map<String, dynamic>>> getBookings({
    required String memberId,
    String? status,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) queryParams['status'] = status;
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final response = await _httpClient.get(
        ApiConstants.memberBookings(memberId),
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get bookings';
    }
  }

  /// Get member analytics/stats
  Future<Map<String, dynamic>> getStats(String memberId) async {
    try {
      final response = await _httpClient.get('/members/$memberId/stats');
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get stats';
    }
  }

  /// Update body measurements
  Future<void> updateMeasurements({
    required String memberId,
    double? weight,
    double? bodyFat,
    double? muscleMass,
    Map<String, double>? measurements,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (weight != null) data['weight'] = weight;
      if (bodyFat != null) data['body_fat'] = bodyFat;
      if (muscleMass != null) data['muscle_mass'] = muscleMass;
      if (measurements != null) data['measurements'] = measurements;

      await _httpClient.post(
        '/members/$memberId/measurements',
        data: data,
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to update measurements';
    }
  }

  /// Upload progress photo
  Future<String> uploadProgressPhoto({
    required String memberId,
    required String filePath,
    String? notes,
  }) async {
    try {
      final response = await _httpClient.uploadFile(
        '/members/$memberId/progress-photos',
        filePath,
        data: notes != null ? {'notes': notes} : null,
      );

      return response.data['photo_url'];
    } on DioException catch (e) {
      throw e.error ?? 'Failed to upload progress photo';
    }
  }

  /// Get progress photos
  Future<List<Map<String, dynamic>>> getProgressPhotos(String memberId) async {
    try {
      final response = await _httpClient.get('/members/$memberId/progress-photos');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get progress photos';
    }
  }
}
