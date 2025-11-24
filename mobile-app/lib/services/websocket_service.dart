import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

enum WebSocketStatus {
  connecting,
  connected,
  disconnected,
  error,
}

class WebSocketService {
  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>>? _messageController;
  StreamController<WebSocketStatus>? _statusController;
  Timer? _reconnectTimer;
  Timer? _heartbeatTimer;
  bool _shouldReconnect = true;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 5;
  static const Duration _reconnectDelay = Duration(seconds: 3);
  static const Duration _heartbeatInterval = Duration(seconds: 30);

  /// Get message stream
  Stream<Map<String, dynamic>> get messageStream {
    _messageController ??= StreamController<Map<String, dynamic>>.broadcast();
    return _messageController!.stream;
  }

  /// Get status stream
  Stream<WebSocketStatus> get statusStream {
    _statusController ??= StreamController<WebSocketStatus>.broadcast();
    return _statusController!.stream;
  }

  /// Connect to WebSocket
  Future<void> connect() async {
    try {
      // Get access token
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(AppConfig.accessTokenKey);

      if (token == null) {
        throw 'No access token available';
      }

      // Build WebSocket URL
      final wsUrl = AppConfig.apiBaseUrl
          .replaceFirst('http://', 'ws://')
          .replaceFirst('https://', 'wss://');

      final uri = Uri.parse('$wsUrl${AppConfig.apiPrefix}/ws?token=$token');

      // Update status
      _updateStatus(WebSocketStatus.connecting);

      // Create WebSocket connection
      _channel = WebSocketChannel.connect(uri);

      // Listen to messages
      _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnect,
        cancelOnError: false,
      );

      // Update status
      _updateStatus(WebSocketStatus.connected);
      _reconnectAttempts = 0;

      // Start heartbeat
      _startHeartbeat();

      print('WebSocket connected successfully');
    } catch (e) {
      print('WebSocket connection error: $e');
      _updateStatus(WebSocketStatus.error);
      _scheduleReconnect();
    }
  }

  /// Disconnect WebSocket
  void disconnect() {
    _shouldReconnect = false;
    _reconnectTimer?.cancel();
    _heartbeatTimer?.cancel();
    _channel?.sink.close();
    _updateStatus(WebSocketStatus.disconnected);
  }

  /// Send message
  void send(Map<String, dynamic> message) {
    if (_channel != null) {
      _channel!.sink.add(json.encode(message));
    } else {
      print('WebSocket not connected');
    }
  }

  /// Subscribe to event
  void subscribe(String event) {
    send({
      'type': 'subscribe',
      'event': event,
    });
  }

  /// Unsubscribe from event
  void unsubscribe(String event) {
    send({
      'type': 'unsubscribe',
      'event': event,
    });
  }

  /// Handle incoming message
  void _handleMessage(dynamic message) {
    try {
      final data = json.decode(message as String) as Map<String, dynamic>;
      _messageController?.add(data);

      // Handle heartbeat response
      if (data['type'] == 'pong') {
        print('Heartbeat acknowledged');
      }
    } catch (e) {
      print('Error parsing WebSocket message: $e');
    }
  }

  /// Handle error
  void _handleError(dynamic error) {
    print('WebSocket error: $error');
    _updateStatus(WebSocketStatus.error);
    _scheduleReconnect();
  }

  /// Handle disconnect
  void _handleDisconnect() {
    print('WebSocket disconnected');
    _updateStatus(WebSocketStatus.disconnected);
    _heartbeatTimer?.cancel();

    if (_shouldReconnect) {
      _scheduleReconnect();
    }
  }

  /// Schedule reconnection
  void _scheduleReconnect() {
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      print('Max reconnection attempts reached');
      _updateStatus(WebSocketStatus.error);
      return;
    }

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(_reconnectDelay * (_reconnectAttempts + 1), () {
      _reconnectAttempts++;
      print('Attempting to reconnect... (Attempt $_reconnectAttempts)');
      connect();
    });
  }

  /// Start heartbeat
  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(_heartbeatInterval, (timer) {
      send({'type': 'ping'});
    });
  }

  /// Update status
  void _updateStatus(WebSocketStatus status) {
    _statusController?.add(status);
  }

  /// Dispose
  void dispose() {
    disconnect();
    _messageController?.close();
    _statusController?.close();
    _reconnectTimer?.cancel();
    _heartbeatTimer?.cancel();
  }

  // ==================== Specific Event Subscriptions ====================

  /// Subscribe to check-in updates
  void subscribeToCheckIns() {
    subscribe('check_ins');
  }

  /// Subscribe to class booking updates
  void subscribeToBookings() {
    subscribe('bookings');
  }

  /// Subscribe to membership updates
  void subscribeToMembership() {
    subscribe('membership');
  }

  /// Subscribe to notifications
  void subscribeToNotifications() {
    subscribe('notifications');
  }

  /// Subscribe to payment updates
  void subscribeToPayments() {
    subscribe('payments');
  }

  /// Subscribe to all events for member
  void subscribeToAll() {
    subscribeToCheckIns();
    subscribeToBookings();
    subscribeToMembership();
    subscribeToNotifications();
    subscribeToPayments();
  }

  /// Unsubscribe from all events
  void unsubscribeFromAll() {
    unsubscribe('check_ins');
    unsubscribe('bookings');
    unsubscribe('membership');
    unsubscribe('notifications');
    unsubscribe('payments');
  }
}

/// Singleton instance
final webSocketService = WebSocketService();
