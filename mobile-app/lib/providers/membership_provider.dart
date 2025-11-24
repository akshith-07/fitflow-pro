import 'package:flutter/foundation.dart';
import '../models/membership.dart';
import '../services/http_client.dart';

class MembershipProvider with ChangeNotifier {
  Membership? _currentMembership;
  List<MembershipPlan> _plans = [];
  bool _isLoading = false;
  String? _error;

  Membership? get currentMembership => _currentMembership;
  List<MembershipPlan> get plans => _plans;
  bool get isLoading => _isLoading;
  String? get error => _error;

  final ApiClient _apiClient = ApiClient();

  Future<void> fetchCurrentMembership() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiClient.get('/memberships/current');
      if (response != null) {
        _currentMembership = Membership.fromJson(response);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchPlans() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiClient.get('/membership-plans');
      if (response != null && response is List) {
        _plans = response.map((json) => MembershipPlan.fromJson(json)).toList();
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> freezeMembership(DateTime startDate, DateTime endDate) async {
    _isLoading = true;
    notifyListeners();

    try {
      await _apiClient.post('/memberships/${_currentMembership!.id}/freeze', {
        'freeze_start_date': startDate.toIso8601String(),
        'freeze_end_date': endDate.toIso8601String(),
      });

      await fetchCurrentMembership();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> cancelMembership(String reason) async {
    _isLoading = true;
    notifyListeners();

    try {
      await _apiClient.post('/memberships/${_currentMembership!.id}/cancel', {
        'cancellation_reason': reason,
      });

      await fetchCurrentMembership();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> upgradeMembership(String planId) async {
    _isLoading = true;
    notifyListeners();

    try {
      await _apiClient.post('/memberships/${_currentMembership!.id}/upgrade', {
        'new_plan_id': planId,
      });

      await fetchCurrentMembership();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
}
