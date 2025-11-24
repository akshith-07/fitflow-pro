class ApiConstants {
  // Auth Endpoints
  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String refresh = '/auth/refresh';
  static const String logout = '/auth/logout';
  static const String forgotPassword = '/auth/forgot-password';
  static const String resetPassword = '/auth/reset-password';
  static const String verifyEmail = '/auth/verify-email';

  // Member Endpoints
  static const String members = '/members';
  static String memberById(String id) => '/members/$id';
  static String memberAttendance(String id) => '/members/$id/attendance';
  static String memberPayments(String id) => '/members/$id/payments';
  static String memberBookings(String id) => '/members/$id/bookings';

  // Membership Endpoints
  static const String membershipPlans = '/membership-plans';
  static String membershipPlanById(String id) => '/membership-plans/$id';
  static const String memberships = '/memberships';
  static String membershipById(String id) => '/memberships/$id';
  static String membershipRenew(String id) => '/memberships/$id/renew';
  static String membershipFreeze(String id) => '/memberships/$id/freeze';
  static String membershipCancel(String id) => '/memberships/$id/cancel';

  // Check-in Endpoints
  static const String checkIns = '/check-ins';
  static String checkInById(String id) => '/check-ins/$id';
  static const String checkInCurrent = '/check-ins/current';
  static String checkInByMember(String memberId) => '/check-ins/member/$memberId';
  static const String checkInQrValidate = '/check-ins/qr-validate';
  static const String checkInBiometric = '/check-ins/biometric';

  // Class Endpoints
  static const String classes = '/classes';
  static String classById(String id) => '/classes/$id';
  static const String classSchedule = '/classes/schedule';
  static String classBook(String id) => '/classes/$id/book';
  static String classCancelBooking(String scheduleId) => '/classes/$scheduleId/cancel-booking';
  static String classAttendance(String id) => '/classes/$id/attendance';
  static String classWaitlist(String id) => '/classes/$id/waitlist';

  // Trainer Endpoints
  static const String trainers = '/trainers';
  static String trainerById(String id) => '/trainers/$id';
  static String trainerSchedule(String id) => '/trainers/$id/schedule';
  static String trainerClients(String id) => '/trainers/$id/clients';
  static String trainerSessions(String id) => '/trainers/$id/sessions';

  // Payment Endpoints
  static const String payments = '/payments';
  static String paymentById(String id) => '/payments/$id';
  static const String paymentWebhook = '/payments/webhook';
  static String paymentRefund(String id) => '/payments/$id/refund';
  static const String paymentPending = '/payments/pending';
  static String paymentRetry(String id) => '/payments/$id/retry';

  // Invoice Endpoints
  static const String invoices = '/invoices';
  static String invoiceById(String id) => '/invoices/$id';
  static String invoiceSend(String id) => '/invoices/$id/send';
  static String invoiceMarkPaid(String id) => '/invoices/$id/mark-paid';
  static String invoicePdf(String id) => '/invoices/$id/pdf';

  // Notification Endpoints
  static const String notifications = '/notifications';
  static String notificationById(String id) => '/notifications/$id';
  static const String notificationSend = '/notifications/send';
  static const String notificationBulk = '/notifications/bulk';
  static const String notificationTemplates = '/notifications/templates';
  static const String notificationHistory = '/notifications/history';

  // Analytics Endpoints
  static const String analyticsDashboard = '/analytics/dashboard';
  static const String analyticsRevenue = '/analytics/revenue';
  static const String analyticsMembers = '/analytics/members';
  static const String analyticsAttendance = '/analytics/attendance';
  static const String analyticsClasses = '/analytics/classes';

  // Report Endpoints
  static const String reportsGenerate = '/reports/generate';
  static const String reportsScheduled = '/reports/scheduled';
  static String reportById(String id) => '/reports/$id';
  static String reportDownload(String id) => '/reports/$id/download';

  // Equipment Endpoints
  static const String equipment = '/equipment';
  static String equipmentById(String id) => '/equipment/$id';

  // Organization Endpoints
  static const String organizations = '/organizations';
  static String organizationById(String id) => '/organizations/$id';
  static String organizationSettings(String id) => '/organizations/$id/settings';

  // Leads Endpoints
  static const String leads = '/leads';
  static String leadById(String id) => '/leads/$id';
  static String leadConvert(String id) => '/leads/$id/convert';
}
