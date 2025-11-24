class AppConstants {
  // App Strings
  static const String appName = 'FitFlow Pro';
  static const String appTagline = 'Your fitness journey starts here';

  // Validation Messages
  static const String requiredField = 'This field is required';
  static const String invalidEmail = 'Please enter a valid email';
  static const String invalidPhone = 'Please enter a valid phone number';
  static const String passwordTooShort = 'Password must be at least 8 characters';
  static const String passwordsDontMatch = 'Passwords do not match';

  // Success Messages
  static const String loginSuccess = 'Login successful';
  static const String registerSuccess = 'Registration successful';
  static const String checkInSuccess = 'Checked in successfully';
  static const String bookingSuccess = 'Class booked successfully';
  static const String bookingCancelled = 'Booking cancelled';
  static const String profileUpdated = 'Profile updated successfully';

  // Error Messages
  static const String genericError = 'Something went wrong. Please try again.';
  static const String networkError = 'No internet connection';
  static const String serverError = 'Server error. Please try again later.';
  static const String unauthorized = 'Session expired. Please login again.';
  static const String notFound = 'Resource not found';
  static const String invalidCredentials = 'Invalid email or password';

  // Button Labels
  static const String login = 'Login';
  static const String register = 'Register';
  static const String submit = 'Submit';
  static const String cancel = 'Cancel';
  static const String save = 'Save';
  static const String delete = 'Delete';
  static const String edit = 'Edit';
  static const String confirm = 'Confirm';
  static const String retry = 'Retry';
  static const String getStarted = 'Get Started';
  static const String continueText = 'Continue';
  static const String skip = 'Skip';
  static const String done = 'Done';

  // Navigation Labels
  static const String home = 'Home';
  static const String classes = 'Classes';
  static const String checkIn = 'Check-In';
  static const String progress = 'Progress';
  static const String profile = 'Profile';

  // Time Formats
  static const String timeFormat12 = 'hh:mm a';
  static const String timeFormat24 = 'HH:mm';
  static const String dateFormat = 'MMM dd, yyyy';
  static const String dateTimeFormat = 'MMM dd, yyyy hh:mm a';
  static const String shortDateFormat = 'MM/dd/yyyy';

  // Membership Status
  static const String membershipActive = 'active';
  static const String membershipFrozen = 'frozen';
  static const String membershipExpired = 'expired';
  static const String membershipCancelled = 'cancelled';

  // Class Booking Status
  static const String bookingBooked = 'booked';
  static const String bookingAttended = 'attended';
  static const String bookingNoShow = 'no_show';
  static const String bookingCancelledStatus = 'cancelled';
  static const String bookingWaitlisted = 'waitlisted';

  // Payment Status
  static const String paymentPending = 'pending';
  static const String paymentProcessing = 'processing';
  static const String paymentCompleted = 'completed';
  static const String paymentFailed = 'failed';
  static const String paymentRefunded = 'refunded';

  // Check-in Methods
  static const String checkInQr = 'qr';
  static const String checkInNfc = 'nfc';
  static const String checkInManual = 'manual';
  static const String checkInBiometric = 'biometric';
  static const String checkInApp = 'app';

  // Difficulty Levels
  static const String difficultyBeginner = 'beginner';
  static const String difficultyIntermediate = 'intermediate';
  static const String difficultyAdvanced = 'advanced';

  // Gender
  static const String genderMale = 'male';
  static const String genderFemale = 'female';
  static const String genderOther = 'other';
  static const String genderNotSpecified = 'not_specified';

  // User Roles
  static const String roleSuperAdmin = 'super_admin';
  static const String roleGymOwner = 'gym_owner';
  static const String roleAdmin = 'admin';
  static const String roleTrainer = 'trainer';
  static const String roleReceptionist = 'receptionist';
  static const String roleMember = 'member';

  // Animation Durations (milliseconds)
  static const int animationShort = 200;
  static const int animationMedium = 300;
  static const int animationLong = 500;

  // Debounce Duration (milliseconds)
  static const int debounceDuration = 500;

  // Image Quality
  static const int imageQualityLow = 50;
  static const int imageQualityMedium = 75;
  static const int imageQualityHigh = 90;

  // Max Image Size (MB)
  static const int maxImageSize = 5;

  // Notification Types
  static const String notificationEmail = 'email';
  static const String notificationSms = 'sms';
  static const String notificationPush = 'push';
  static const String notificationWhatsapp = 'whatsapp';

  // Local Storage Keys (in addition to app_config.dart)
  static const String languageKey = 'language';
  static const String notificationsEnabledKey = 'notifications_enabled';
  static const String soundEnabledKey = 'sound_enabled';
  static const String vibrationEnabledKey = 'vibration_enabled';

  // Regex Patterns
  static final RegExp emailRegex = RegExp(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
  );
  static final RegExp phoneRegex = RegExp(
    r'^\+?[1-9]\d{1,14}$',
  );
  static final RegExp passwordRegex = RegExp(
    r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$',
  );
}
