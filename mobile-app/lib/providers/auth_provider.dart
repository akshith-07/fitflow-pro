import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/member.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  User? _user;
  Member? _member;
  String? _token;
  bool _isLoading = false;
  String? _error;

  User? get user => _user;
  Member? get member => _member;
  String? get token => _token;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _user != null && _token != null;

  final AuthService _authService = AuthService();

  AuthProvider() {
    _loadStoredAuth();
  }

  Future<void> _loadStoredAuth() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    final userJson = prefs.getString('user');
    final memberJson = prefs.getString('member');

    if (_token != null && userJson != null) {
      // In real app, validate token with backend
      // For now, just restore from storage
      notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _authService.login(email, password);
      _user = response['user'] != null ? User.fromJson(response['user']) : null;
      _member =
          response['member'] != null ? Member.fromJson(response['member']) : null;
      _token = response['token'];

      // Store in SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _token!);
      if (_user != null) {
        await prefs.setString('user', _user.toString());
      }
      if (_member != null) {
        await prefs.setString('member', _member.toString());
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String phone,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _authService.register(
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
        phone: phone,
      );

      _user = response['user'] != null ? User.fromJson(response['user']) : null;
      _member =
          response['member'] != null ? Member.fromJson(response['member']) : null;
      _token = response['token'];

      // Store in SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _token!);

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    _user = null;
    _member = null;
    _token = null;

    // Clear SharedPreferences
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();

    notifyListeners();
  }

  Future<bool> updateProfile(Map<String, dynamic> data) async {
    _isLoading = true;
    notifyListeners();

    try {
      // Call API to update profile
      // final response = await _authService.updateProfile(data);
      // Update local user/member data

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
