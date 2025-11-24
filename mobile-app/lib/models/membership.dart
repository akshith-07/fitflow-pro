class Membership {
  final String id;
  final String memberId;
  final String planId;
  final String planName;
  final DateTime startDate;
  final DateTime endDate;
  final bool autoRenew;
  final MembershipStatus status;
  final DateTime? freezeStartDate;
  final DateTime? freezeEndDate;
  final String? cancellationReason;

  Membership({
    required this.id,
    required this.memberId,
    required this.planId,
    required this.planName,
    required this.startDate,
    required this.endDate,
    required this.autoRenew,
    required this.status,
    this.freezeStartDate,
    this.freezeEndDate,
    this.cancellationReason,
  });

  factory Membership.fromJson(Map<String, dynamic> json) {
    return Membership(
      id: json['id'],
      memberId: json['member_id'],
      planId: json['plan_id'],
      planName: json['plan_name'] ?? '',
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      autoRenew: json['auto_renew'] ?? false,
      status: MembershipStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => MembershipStatus.active,
      ),
      freezeStartDate: json['freeze_start_date'] != null
          ? DateTime.parse(json['freeze_start_date'])
          : null,
      freezeEndDate: json['freeze_end_date'] != null
          ? DateTime.parse(json['freeze_end_date'])
          : null,
      cancellationReason: json['cancellation_reason'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'member_id': memberId,
      'plan_id': planId,
      'plan_name': planName,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
      'auto_renew': autoRenew,
      'status': status.name,
      'freeze_start_date': freezeStartDate?.toIso8601String(),
      'freeze_end_date': freezeEndDate?.toIso8601String(),
      'cancellation_reason': cancellationReason,
    };
  }

  int get daysRemaining {
    final now = DateTime.now();
    if (now.isAfter(endDate)) return 0;
    return endDate.difference(now).inDays;
  }

  bool get isExpired => DateTime.now().isAfter(endDate);
  bool get isActive => status == MembershipStatus.active && !isExpired;
}

enum MembershipStatus {
  active,
  frozen,
  expired,
  cancelled,
}

class MembershipPlan {
  final String id;
  final String name;
  final String description;
  final double price;
  final int durationDays;
  final String durationType;
  final double setupFee;
  final List<String> features;
  final Map<String, dynamic>? accessHours;
  final bool isActive;

  MembershipPlan({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.durationDays,
    required this.durationType,
    required this.setupFee,
    required this.features,
    this.accessHours,
    required this.isActive,
  });

  factory MembershipPlan.fromJson(Map<String, dynamic> json) {
    return MembershipPlan(
      id: json['id'],
      name: json['name'],
      description: json['description'] ?? '',
      price: (json['price'] ?? 0).toDouble(),
      durationDays: json['duration_days'] ?? 30,
      durationType: json['duration_type'] ?? 'monthly',
      setupFee: (json['setup_fee'] ?? 0).toDouble(),
      features: List<String>.from(json['features'] ?? []),
      accessHours: json['access_hours'],
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'price': price,
      'duration_days': durationDays,
      'duration_type': durationType,
      'setup_fee': setupFee,
      'features': features,
      'access_hours': accessHours,
      'is_active': isActive,
    };
  }
}
