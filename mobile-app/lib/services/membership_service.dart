import 'package:dio/dio.dart';
import 'http_client.dart';
import '../constants/api_constants.dart';
import '../models/membership.dart';

class MembershipService {
  final HttpClient _httpClient = HttpClient();

  /// Get all available membership plans
  Future<List<Map<String, dynamic>>> getPlans() async {
    try {
      final response = await _httpClient.get(ApiConstants.membershipPlans);
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get membership plans';
    }
  }

  /// Get specific membership plan details
  Future<Map<String, dynamic>> getPlanById(String planId) async {
    try {
      final response = await _httpClient.get(
        ApiConstants.membershipPlanById(planId),
      );
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get plan details';
    }
  }

  /// Get current membership
  Future<Membership> getCurrentMembership() async {
    try {
      final response = await _httpClient.get('/memberships/current');
      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get current membership';
    }
  }

  /// Get membership by ID
  Future<Membership> getMembershipById(String membershipId) async {
    try {
      final response = await _httpClient.get(
        ApiConstants.membershipById(membershipId),
      );
      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get membership';
    }
  }

  /// Purchase/upgrade membership plan
  Future<Map<String, dynamic>> purchaseMembership({
    required String planId,
    String? paymentMethodId,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.memberships,
        data: {
          'plan_id': planId,
          'payment_method_id': paymentMethodId,
          'metadata': metadata,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to purchase membership';
    }
  }

  /// Upgrade membership
  Future<Membership> upgradeMembership({
    required String membershipId,
    required String newPlanId,
    bool prorated = true,
  }) async {
    try {
      final response = await _httpClient.post(
        '/memberships/$membershipId/upgrade',
        data: {
          'new_plan_id': newPlanId,
          'prorated': prorated,
        },
      );

      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to upgrade membership';
    }
  }

  /// Downgrade membership (effective next billing cycle)
  Future<Membership> downgradeMembership({
    required String membershipId,
    required String newPlanId,
  }) async {
    try {
      final response = await _httpClient.post(
        '/memberships/$membershipId/downgrade',
        data: {'new_plan_id': newPlanId},
      );

      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to downgrade membership';
    }
  }

  /// Renew membership
  Future<Membership> renewMembership({
    required String membershipId,
    String? paymentMethodId,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.membershipRenew(membershipId),
        data: {'payment_method_id': paymentMethodId},
      );

      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to renew membership';
    }
  }

  /// Freeze membership
  Future<Membership> freezeMembership({
    required String membershipId,
    required DateTime startDate,
    required DateTime endDate,
    String? reason,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.membershipFreeze(membershipId),
        data: {
          'start_date': startDate.toIso8601String(),
          'end_date': endDate.toIso8601String(),
          'reason': reason,
        },
      );

      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to freeze membership';
    }
  }

  /// Unfreeze membership
  Future<Membership> unfreezeMembership(String membershipId) async {
    try {
      final response = await _httpClient.post(
        '/memberships/$membershipId/unfreeze',
      );

      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to unfreeze membership';
    }
  }

  /// Cancel membership
  Future<Membership> cancelMembership({
    required String membershipId,
    required String reason,
    bool immediate = false,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.membershipCancel(membershipId),
        data: {
          'reason': reason,
          'immediate': immediate,
        },
      );

      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to cancel membership';
    }
  }

  /// Get freeze policy for membership
  Future<Map<String, dynamic>> getFreezePolicy(String planId) async {
    try {
      final response = await _httpClient.get(
        '/membership-plans/$planId/freeze-policy',
      );
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get freeze policy';
    }
  }

  /// Calculate freeze cost
  Future<Map<String, dynamic>> calculateFreezeCost({
    required String membershipId,
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    try {
      final response = await _httpClient.post(
        '/memberships/$membershipId/calculate-freeze-cost',
        data: {
          'start_date': startDate.toIso8601String(),
          'end_date': endDate.toIso8601String(),
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to calculate freeze cost';
    }
  }

  /// Get cancellation policy
  Future<Map<String, dynamic>> getCancellationPolicy(String planId) async {
    try {
      final response = await _httpClient.get(
        '/membership-plans/$planId/cancellation-policy',
      );
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get cancellation policy';
    }
  }

  /// Enable/disable auto-renewal
  Future<Membership> setAutoRenew({
    required String membershipId,
    required bool autoRenew,
  }) async {
    try {
      final response = await _httpClient.patch(
        ApiConstants.membershipById(membershipId),
        data: {'auto_renew': autoRenew},
      );

      return Membership.fromJson(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to update auto-renewal';
    }
  }

  /// Get membership history
  Future<List<Membership>> getMembershipHistory() async {
    try {
      final response = await _httpClient.get('/memberships/history');
      return (response.data as List)
          .map((json) => Membership.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get membership history';
    }
  }
}
