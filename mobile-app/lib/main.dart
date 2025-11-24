import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:firebase_core/firebase_core.dart';
import 'config/app_theme.dart';
import 'providers/auth_provider.dart';
import 'providers/theme_provider.dart';
import 'providers/membership_provider.dart';
import 'providers/workout_provider.dart';
import 'screens/auth/splash_screen.dart';
import 'services/storage_service.dart';
import 'services/notification_service.dart';
import 'services/websocket_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  // Initialize storage (Hive)
  try {
    await StorageService.initialize();
    print('Storage initialized successfully');
  } catch (e) {
    print('Error initializing storage: $e');
  }

  // Initialize Firebase
  try {
    await Firebase.initializeApp();
    print('Firebase initialized successfully');

    // Initialize notification service
    final notificationService = NotificationService();
    await notificationService.initialize();
    print('Notification service initialized successfully');
  } catch (e) {
    print('Error initializing Firebase/Notifications: $e');
  }

  runApp(const FitFlowMemberApp());
}

class FitFlowMemberApp extends StatelessWidget {
  const FitFlowMemberApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => MembershipProvider()),
        ChangeNotifierProvider(create: (_) => WorkoutProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, child) {
          return MaterialApp(
            title: 'FitFlow Pro - Member',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeProvider.themeMode,
            home: const SplashScreen(),
          );
        },
      ),
    );
  }
}
