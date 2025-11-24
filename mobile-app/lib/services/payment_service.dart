import 'package:dio/dio.dart';
import 'http_client.dart';
import '../constants/api_constants.dart';

class PaymentService {
  final HttpClient _httpClient = HttpClient();

  /// Get payment methods
  Future<List<Map<String, dynamic>>> getPaymentMethods() async {
    try {
      final response = await _httpClient.get('/payments/methods');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get payment methods';
    }
  }

  /// Add payment method
  Future<Map<String, dynamic>> addPaymentMethod({
    required String type,
    required Map<String, dynamic> details,
  }) async {
    try {
      final response = await _httpClient.post(
        '/payments/methods',
        data: {
          'type': type,
          'details': details,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to add payment method';
    }
  }

  /// Remove payment method
  Future<void> removePaymentMethod(String methodId) async {
    try {
      await _httpClient.delete('/payments/methods/$methodId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to remove payment method';
    }
  }

  /// Set default payment method
  Future<void> setDefaultPaymentMethod(String methodId) async {
    try {
      await _httpClient.post(
        '/payments/methods/$methodId/set-default',
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to set default payment method';
    }
  }

  /// Create payment
  Future<Map<String, dynamic>> createPayment({
    required double amount,
    required String currency,
    required String membershipId,
    String? paymentMethodId,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.payments,
        data: {
          'amount': amount,
          'currency': currency,
          'membership_id': membershipId,
          'payment_method_id': paymentMethodId,
          'metadata': metadata,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to create payment';
    }
  }

  /// Get payment history
  Future<List<Map<String, dynamic>>> getPaymentHistory({
    int? limit,
    int? offset,
    String? status,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;
      if (status != null) queryParams['status'] = status;

      final response = await _httpClient.get(
        ApiConstants.payments,
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get payment history';
    }
  }

  /// Get payment by ID
  Future<Map<String, dynamic>> getPaymentById(String paymentId) async {
    try {
      final response = await _httpClient.get(
        ApiConstants.paymentById(paymentId),
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get payment';
    }
  }

  /// Get pending payments
  Future<List<Map<String, dynamic>>> getPendingPayments() async {
    try {
      final response = await _httpClient.get(ApiConstants.paymentPending);
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get pending payments';
    }
  }

  /// Retry failed payment
  Future<Map<String, dynamic>> retryPayment(String paymentId) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.paymentRetry(paymentId),
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to retry payment';
    }
  }

  /// Request refund
  Future<Map<String, dynamic>> requestRefund({
    required String paymentId,
    String? reason,
  }) async {
    try {
      final response = await _httpClient.post(
        ApiConstants.paymentRefund(paymentId),
        data: {'reason': reason},
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to request refund';
    }
  }

  /// Get invoices
  Future<List<Map<String, dynamic>>> getInvoices({
    int? limit,
    int? offset,
    String? status,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;
      if (status != null) queryParams['status'] = status;

      final response = await _httpClient.get(
        ApiConstants.invoices,
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get invoices';
    }
  }

  /// Get invoice by ID
  Future<Map<String, dynamic>> getInvoiceById(String invoiceId) async {
    try {
      final response = await _httpClient.get(
        ApiConstants.invoiceById(invoiceId),
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get invoice';
    }
  }

  /// Download invoice PDF
  Future<String> downloadInvoicePdf(String invoiceId) async {
    try {
      final response = await _httpClient.get(
        ApiConstants.invoicePdf(invoiceId),
      );

      return response.data['pdf_url'];
    } on DioException catch (e) {
      throw e.error ?? 'Failed to download invoice';
    }
  }

  /// Send invoice to email
  Future<void> sendInvoiceEmail(String invoiceId) async {
    try {
      await _httpClient.post(
        ApiConstants.invoiceSend(invoiceId),
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to send invoice';
    }
  }

  /// Create Stripe payment intent
  Future<Map<String, dynamic>> createStripePaymentIntent({
    required double amount,
    required String currency,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _httpClient.post(
        '/payments/stripe/create-intent',
        data: {
          'amount': amount,
          'currency': currency,
          'metadata': metadata,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to create payment intent';
    }
  }

  /// Confirm Stripe payment
  Future<Map<String, dynamic>> confirmStripePayment({
    required String paymentIntentId,
    required String paymentMethodId,
  }) async {
    try {
      final response = await _httpClient.post(
        '/payments/stripe/confirm',
        data: {
          'payment_intent_id': paymentIntentId,
          'payment_method_id': paymentMethodId,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to confirm payment';
    }
  }

  /// Create Razorpay order
  Future<Map<String, dynamic>> createRazorpayOrder({
    required double amount,
    required String currency,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _httpClient.post(
        '/payments/razorpay/create-order',
        data: {
          'amount': amount,
          'currency': currency,
          'metadata': metadata,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to create order';
    }
  }

  /// Verify Razorpay payment
  Future<Map<String, dynamic>> verifyRazorpayPayment({
    required String orderId,
    required String paymentId,
    required String signature,
  }) async {
    try {
      final response = await _httpClient.post(
        '/payments/razorpay/verify',
        data: {
          'order_id': orderId,
          'payment_id': paymentId,
          'signature': signature,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Payment verification failed';
    }
  }

  /// Get payment summary/stats
  Future<Map<String, dynamic>> getPaymentSummary() async {
    try {
      final response = await _httpClient.get('/payments/summary');
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get payment summary';
    }
  }
}
