import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeProvider with ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.system;
  bool _useSystemTheme = true;

  ThemeMode get themeMode => _themeMode;
  bool get useSystemTheme => _useSystemTheme;
  bool get isDarkMode => _themeMode == ThemeMode.dark;

  ThemeProvider() {
    _loadThemePreference();
  }

  Future<void> _loadThemePreference() async {
    final prefs = await SharedPreferences.getInstance();
    _useSystemTheme = prefs.getBool('use_system_theme') ?? true;

    if (!_useSystemTheme) {
      final isDark = prefs.getBool('is_dark_mode') ?? false;
      _themeMode = isDark ? ThemeMode.dark : ThemeMode.light;
    } else {
      _themeMode = ThemeMode.system;
    }

    notifyListeners();
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    _themeMode = mode;
    _useSystemTheme = mode == ThemeMode.system;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('use_system_theme', _useSystemTheme);

    if (!_useSystemTheme) {
      await prefs.setBool('is_dark_mode', mode == ThemeMode.dark);
    }

    notifyListeners();
  }

  Future<void> toggleTheme() async {
    if (_themeMode == ThemeMode.light) {
      await setThemeMode(ThemeMode.dark);
    } else {
      await setThemeMode(ThemeMode.light);
    }
  }
}
