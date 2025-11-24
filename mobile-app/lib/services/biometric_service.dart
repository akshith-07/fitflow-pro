import 'package:local_auth/local_auth.dart';
import 'package:local_auth/error_codes.dart' as auth_error;
import 'package:shared_preferences/shared_preferences.dart';

class BiometricService {
  final LocalAuthentication _localAuth = LocalAuthentication();

  /// Check if device supports biometric authentication
  Future<bool> isDeviceSupported() async {
    try {
      return await _localAuth.isDeviceSupported();
    } catch (e) {
      print('Error checking device support: $e');
      return false;
    }
  }

  /// Check if biometric authentication is available
  Future<bool> isBiometricAvailable() async {
    try {
      return await _localAuth.canCheckBiometrics;
    } catch (e) {
      print('Error checking biometric availability: $e');
      return false;
    }
  }

  /// Get available biometric types
  Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      return await _localAuth.getAvailableBiometrics();
    } catch (e) {
      print('Error getting available biometrics: $e');
      return [];
    }
  }

  /// Authenticate with biometrics
  Future<bool> authenticate({
    String reason = 'Please authenticate to continue',
    bool biometricOnly = false,
    bool sensitiveTransaction = true,
    bool stickyAuth = true,
  }) async {
    try {
      // Check if biometrics are available
      final canAuthenticate = await isBiometricAvailable();
      if (!canAuthenticate) {
        throw 'Biometric authentication is not available on this device';
      }

      // Authenticate
      final authenticated = await _localAuth.authenticate(
        localizedReason: reason,
        options: AuthenticationOptions(
          biometricOnly: biometricOnly,
          sensitiveTransaction: sensitiveTransaction,
          stickyAuth: stickyAuth,
        ),
      );

      return authenticated;
    } catch (e) {
      if (e.toString().contains(auth_error.notAvailable)) {
        throw 'Biometric authentication is not available';
      } else if (e.toString().contains(auth_error.notEnrolled)) {
        throw 'No biometrics enrolled. Please set up biometrics in your device settings';
      } else if (e.toString().contains(auth_error.lockedOut)) {
        throw 'Too many attempts. Biometric authentication is temporarily locked';
      } else if (e.toString().contains(auth_error.permanentlyLockedOut)) {
        throw 'Biometric authentication is permanently locked. Please unlock your device';
      }

      print('Biometric authentication error: $e');
      rethrow;
    }
  }

  /// Authenticate for login
  Future<bool> authenticateForLogin() async {
    return await authenticate(
      reason: 'Authenticate to login to FitFlow Pro',
      biometricOnly: true,
    );
  }

  /// Authenticate for payment
  Future<bool> authenticateForPayment() async {
    return await authenticate(
      reason: 'Authenticate to complete payment',
      biometricOnly: true,
      sensitiveTransaction: true,
    );
  }

  /// Authenticate for sensitive action
  Future<bool> authenticateForSensitiveAction(String action) async {
    return await authenticate(
      reason: 'Authenticate to $action',
      biometricOnly: false,
      sensitiveTransaction: true,
    );
  }

  /// Stop authentication (cancel)
  Future<void> stopAuthentication() async {
    try {
      await _localAuth.stopAuthentication();
    } catch (e) {
      print('Error stopping authentication: $e');
    }
  }

  /// Enable biometric login
  Future<void> enableBiometricLogin() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('biometric_login_enabled', true);
  }

  /// Disable biometric login
  Future<void> disableBiometricLogin() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('biometric_login_enabled', false);
  }

  /// Check if biometric login is enabled
  Future<bool> isBiometricLoginEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool('biometric_login_enabled') ?? false;
  }

  /// Get biometric type name for UI
  Future<String> getBiometricTypeName() async {
    final biometrics = await getAvailableBiometrics();

    if (biometrics.contains(BiometricType.face)) {
      return 'Face ID';
    } else if (biometrics.contains(BiometricType.fingerprint)) {
      return 'Fingerprint';
    } else if (biometrics.contains(BiometricType.iris)) {
      return 'Iris';
    } else if (biometrics.contains(BiometricType.strong)) {
      return 'Biometric';
    } else if (biometrics.contains(BiometricType.weak)) {
      return 'Biometric (Weak)';
    }

    return 'Biometric';
  }

  /// Check if face ID is available (iOS)
  Future<bool> isFaceIDAvailable() async {
    final biometrics = await getAvailableBiometrics();
    return biometrics.contains(BiometricType.face);
  }

  /// Check if fingerprint is available
  Future<bool> isFingerprintAvailable() async {
    final biometrics = await getAvailableBiometrics();
    return biometrics.contains(BiometricType.fingerprint);
  }
}
