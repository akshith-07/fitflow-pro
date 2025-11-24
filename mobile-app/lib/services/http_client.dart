import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

class HttpClient {
  static final HttpClient _instance = HttpClient._internal();
  late Dio dio;

  factory HttpClient() {
    return _instance;
  }

  HttpClient._internal() {
    dio = Dio(
      BaseOptions(
        baseURL: '${AppConfig.apiBaseUrl}${AppConfig.apiPrefix}',
        connectTimeout: Duration(seconds: AppConfig.connectionTimeout),
        receiveTimeout: Duration(seconds: AppConfig.receiveTimeout),
        sendTimeout: Duration(seconds: AppConfig.sendTimeout),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add interceptors
    dio.interceptors.add(_AuthInterceptor());

    // Add logger in debug mode
    if (AppConfig.enableNetworkLogging && AppConfig.isDebugMode) {
      dio.interceptors.add(
        PrettyDioLogger(
          requestHeader: true,
          requestBody: true,
          responseBody: true,
          responseHeader: false,
          error: true,
          compact: true,
          maxWidth: 90,
        ),
      );
    }

    // Add error interceptor
    dio.interceptors.add(_ErrorInterceptor());
  }

  // GET Request
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  // POST Request
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  // PUT Request
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  // DELETE Request
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  // PATCH Request
  Future<Response> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  // Upload File
  Future<Response> uploadFile(
    String path,
    String filePath, {
    Map<String, dynamic>? data,
    ProgressCallback? onSendProgress,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath),
        ...?data,
      });

      final response = await dio.post(
        path,
        data: formData,
        onSendProgress: onSendProgress,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }
}

// Auth Interceptor - Adds JWT token to requests
class _AuthInterceptor extends Interceptor {
  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(AppConfig.accessTokenKey);

    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // Handle 401 Unauthorized - Token expired
    if (err.response?.statusCode == 401) {
      final prefs = await SharedPreferences.getInstance();
      final refreshToken = prefs.getString(AppConfig.refreshTokenKey);

      if (refreshToken != null) {
        try {
          // Attempt to refresh token
          final dio = Dio(BaseOptions(
            baseURL: '${AppConfig.apiBaseUrl}${AppConfig.apiPrefix}',
          ));

          final response = await dio.post(
            '/auth/refresh',
            data: {'refresh_token': refreshToken},
          );

          if (response.statusCode == 200) {
            final newAccessToken = response.data['access_token'];
            final newRefreshToken = response.data['refresh_token'];

            // Save new tokens
            await prefs.setString(AppConfig.accessTokenKey, newAccessToken);
            await prefs.setString(AppConfig.refreshTokenKey, newRefreshToken);

            // Retry original request with new token
            err.requestOptions.headers['Authorization'] =
                'Bearer $newAccessToken';

            final retryResponse = await dio.fetch(err.requestOptions);
            return handler.resolve(retryResponse);
          }
        } catch (e) {
          // Refresh failed - clear tokens and redirect to login
          await prefs.remove(AppConfig.accessTokenKey);
          await prefs.remove(AppConfig.refreshTokenKey);
          await prefs.remove(AppConfig.userDataKey);
        }
      }
    }

    handler.next(err);
  }
}

// Error Interceptor - Handles common errors
class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    String errorMessage;

    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        errorMessage = 'Connection timeout. Please check your internet connection.';
        break;

      case DioExceptionType.badResponse:
        errorMessage = _handleResponseError(err.response);
        break;

      case DioExceptionType.cancel:
        errorMessage = 'Request cancelled';
        break;

      case DioExceptionType.unknown:
        if (err.message?.contains('SocketException') ?? false) {
          errorMessage = 'No internet connection';
        } else {
          errorMessage = 'An unexpected error occurred';
        }
        break;

      default:
        errorMessage = 'An error occurred';
    }

    // Attach custom error message
    err = err.copyWith(
      error: errorMessage,
    );

    handler.next(err);
  }

  String _handleResponseError(Response? response) {
    if (response == null) {
      return 'No response from server';
    }

    switch (response.statusCode) {
      case 400:
        return response.data['detail'] ?? 'Bad request';
      case 401:
        return 'Unauthorized. Please login again.';
      case 403:
        return 'Access forbidden';
      case 404:
        return 'Resource not found';
      case 500:
      case 502:
      case 503:
        return 'Server error. Please try again later.';
      default:
        return 'An error occurred (${response.statusCode})';
    }
  }
}
