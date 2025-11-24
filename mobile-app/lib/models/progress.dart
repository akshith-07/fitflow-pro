class BodyMeasurement {
  final String id;
  final String memberId;
  final DateTime date;
  final double? weight;
  final double? bodyFat;
  final double? muscleMass;
  final double? bmi;
  final double? chest;
  final double? waist;
  final double? hips;
  final double? biceps;
  final double? thighs;
  final String? notes;

  BodyMeasurement({
    required this.id,
    required this.memberId,
    required this.date,
    this.weight,
    this.bodyFat,
    this.muscleMass,
    this.bmi,
    this.chest,
    this.waist,
    this.hips,
    this.biceps,
    this.thighs,
    this.notes,
  });

  factory BodyMeasurement.fromJson(Map<String, dynamic> json) {
    return BodyMeasurement(
      id: json['id'],
      memberId: json['member_id'],
      date: DateTime.parse(json['date']),
      weight: json['weight']?.toDouble(),
      bodyFat: json['body_fat']?.toDouble(),
      muscleMass: json['muscle_mass']?.toDouble(),
      bmi: json['bmi']?.toDouble(),
      chest: json['chest']?.toDouble(),
      waist: json['waist']?.toDouble(),
      hips: json['hips']?.toDouble(),
      biceps: json['biceps']?.toDouble(),
      thighs: json['thighs']?.toDouble(),
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'member_id': memberId,
      'date': date.toIso8601String(),
      'weight': weight,
      'body_fat': bodyFat,
      'muscle_mass': muscleMass,
      'bmi': bmi,
      'chest': chest,
      'waist': waist,
      'hips': hips,
      'biceps': biceps,
      'thighs': thighs,
      'notes': notes,
    };
  }
}

class ProgressPhoto {
  final String id;
  final String memberId;
  final DateTime date;
  final String photoUrl;
  final PhotoAngle angle;
  final String? notes;

  ProgressPhoto({
    required this.id,
    required this.memberId,
    required this.date,
    required this.photoUrl,
    required this.angle,
    this.notes,
  });

  factory ProgressPhoto.fromJson(Map<String, dynamic> json) {
    return ProgressPhoto(
      id: json['id'],
      memberId: json['member_id'],
      date: DateTime.parse(json['date']),
      photoUrl: json['photo_url'],
      angle: PhotoAngle.values.firstWhere(
        (e) => e.name == json['angle'],
        orElse: () => PhotoAngle.front,
      ),
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'member_id': memberId,
      'date': date.toIso8601String(),
      'photo_url': photoUrl,
      'angle': angle.name,
      'notes': notes,
    };
  }
}

enum PhotoAngle {
  front,
  side,
  back,
}

class FitnessGoal {
  final String id;
  final String memberId;
  final String title;
  final String? description;
  final GoalType type;
  final double? targetValue;
  final double? currentValue;
  final DateTime? targetDate;
  final DateTime createdAt;
  final bool isCompleted;
  final DateTime? completedAt;

  FitnessGoal({
    required this.id,
    required this.memberId,
    required this.title,
    this.description,
    required this.type,
    this.targetValue,
    this.currentValue,
    this.targetDate,
    required this.createdAt,
    required this.isCompleted,
    this.completedAt,
  });

  factory FitnessGoal.fromJson(Map<String, dynamic> json) {
    return FitnessGoal(
      id: json['id'],
      memberId: json['member_id'],
      title: json['title'],
      description: json['description'],
      type: GoalType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => GoalType.weightLoss,
      ),
      targetValue: json['target_value']?.toDouble(),
      currentValue: json['current_value']?.toDouble(),
      targetDate: json['target_date'] != null
          ? DateTime.parse(json['target_date'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
      isCompleted: json['is_completed'] ?? false,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'member_id': memberId,
      'title': title,
      'description': description,
      'type': type.name,
      'target_value': targetValue,
      'current_value': currentValue,
      'target_date': targetDate?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'is_completed': isCompleted,
      'completed_at': completedAt?.toIso8601String(),
    };
  }

  double get progressPercentage {
    if (targetValue == null || currentValue == null) return 0;
    return ((currentValue! / targetValue!) * 100).clamp(0, 100);
  }
}

enum GoalType {
  weightLoss,
  muscleGain,
  strength,
  endurance,
  flexibility,
  general,
}

class CheckIn {
  final String id;
  final String memberId;
  final DateTime checkInTime;
  final DateTime? checkOutTime;
  final CheckInMethod method;
  final String? locationId;

  CheckIn({
    required this.id,
    required this.memberId,
    required this.checkInTime,
    this.checkOutTime,
    required this.method,
    this.locationId,
  });

  factory CheckIn.fromJson(Map<String, dynamic> json) {
    return CheckIn(
      id: json['id'],
      memberId: json['member_id'],
      checkInTime: DateTime.parse(json['check_in_time']),
      checkOutTime: json['check_out_time'] != null
          ? DateTime.parse(json['check_out_time'])
          : null,
      method: CheckInMethod.values.firstWhere(
        (e) => e.name == json['method'],
        orElse: () => CheckInMethod.qr,
      ),
      locationId: json['location_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'member_id': memberId,
      'check_in_time': checkInTime.toIso8601String(),
      'check_out_time': checkOutTime?.toIso8601String(),
      'method': method.name,
      'location_id': locationId,
    };
  }

  Duration? get duration {
    if (checkOutTime == null) return null;
    return checkOutTime!.difference(checkInTime);
  }
}

enum CheckInMethod {
  qr,
  nfc,
  manual,
  biometric,
  app,
}

class Achievement {
  final String id;
  final String title;
  final String description;
  final String iconUrl;
  final AchievementType type;
  final DateTime unlockedAt;

  Achievement({
    required this.id,
    required this.title,
    required this.description,
    required this.iconUrl,
    required this.type,
    required this.unlockedAt,
  });

  factory Achievement.fromJson(Map<String, dynamic> json) {
    return Achievement(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      iconUrl: json['icon_url'],
      type: AchievementType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => AchievementType.checkIn,
      ),
      unlockedAt: DateTime.parse(json['unlocked_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'icon_url': iconUrl,
      'type': type.name,
      'unlocked_at': unlockedAt.toIso8601String(),
    };
  }
}

enum AchievementType {
  checkIn,
  workout,
  streak,
  weight,
  strength,
  milestone,
}
