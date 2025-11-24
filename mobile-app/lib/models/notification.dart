class AppNotification {
  final String id;
  final String memberId;
  final String title;
  final String body;
  final NotificationType type;
  final Map<String, dynamic>? data;
  final DateTime createdAt;
  final bool isRead;
  final DateTime? readAt;

  AppNotification({
    required this.id,
    required this.memberId,
    required this.title,
    required this.body,
    required this.type,
    this.data,
    required this.createdAt,
    this.isRead = false,
    this.readAt,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'],
      memberId: json['member_id'],
      title: json['title'],
      body: json['body'],
      type: NotificationType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => NotificationType.general,
      ),
      data: json['data'],
      createdAt: DateTime.parse(json['created_at']),
      isRead: json['is_read'] ?? false,
      readAt: json['read_at'] != null ? DateTime.parse(json['read_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'member_id': memberId,
      'title': title,
      'body': body,
      'type': type.name,
      'data': data,
      'created_at': createdAt.toIso8601String(),
      'is_read': isRead,
      'read_at': readAt?.toIso8601String(),
    };
  }
}

enum NotificationType {
  classReminder,
  classBooked,
  classCancelled,
  paymentReminder,
  paymentSuccess,
  membershipExpiring,
  achievement,
  milestone,
  socialLike,
  socialComment,
  friendRequest,
  challengeUpdate,
  general,
}
