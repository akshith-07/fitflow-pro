class GymClass {
  final String id;
  final String name;
  final String description;
  final String category;
  final int durationMinutes;
  final int capacity;
  final String instructorId;
  final String instructorName;
  final String? instructorPhoto;
  final String room;
  final DifficultyLevel difficultyLevel;
  final String? imageUrl;
  final bool isRecurring;

  GymClass({
    required this.id,
    required this.name,
    required this.description,
    required this.category,
    required this.durationMinutes,
    required this.capacity,
    required this.instructorId,
    required this.instructorName,
    this.instructorPhoto,
    required this.room,
    required this.difficultyLevel,
    this.imageUrl,
    required this.isRecurring,
  });

  factory GymClass.fromJson(Map<String, dynamic> json) {
    return GymClass(
      id: json['id'],
      name: json['name'],
      description: json['description'] ?? '',
      category: json['category'] ?? '',
      durationMinutes: json['duration_minutes'] ?? 60,
      capacity: json['capacity'] ?? 20,
      instructorId: json['instructor_id'],
      instructorName: json['instructor_name'] ?? '',
      instructorPhoto: json['instructor_photo'],
      room: json['room'] ?? '',
      difficultyLevel: DifficultyLevel.values.firstWhere(
        (e) => e.name == json['difficulty_level'],
        orElse: () => DifficultyLevel.beginner,
      ),
      imageUrl: json['image_url'],
      isRecurring: json['is_recurring'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'category': category,
      'duration_minutes': durationMinutes,
      'capacity': capacity,
      'instructor_id': instructorId,
      'instructor_name': instructorName,
      'instructor_photo': instructorPhoto,
      'room': room,
      'difficulty_level': difficultyLevel.name,
      'image_url': imageUrl,
      'is_recurring': isRecurring,
    };
  }
}

enum DifficultyLevel {
  beginner,
  intermediate,
  advanced,
}

class ClassSchedule {
  final String id;
  final String classId;
  final GymClass? classInfo;
  final String instructorId;
  final String instructorName;
  final String? instructorPhoto;
  final DateTime scheduledDate;
  final String startTime;
  final String endTime;
  final ClassStatus status;
  final int spotsBooked;
  final int capacity;
  final bool isBooked;
  final bool isWaitlisted;

  ClassSchedule({
    required this.id,
    required this.classId,
    this.classInfo,
    required this.instructorId,
    required this.instructorName,
    this.instructorPhoto,
    required this.scheduledDate,
    required this.startTime,
    required this.endTime,
    required this.status,
    required this.spotsBooked,
    required this.capacity,
    this.isBooked = false,
    this.isWaitlisted = false,
  });

  factory ClassSchedule.fromJson(Map<String, dynamic> json) {
    return ClassSchedule(
      id: json['id'],
      classId: json['class_id'],
      classInfo:
          json['class_info'] != null ? GymClass.fromJson(json['class_info']) : null,
      instructorId: json['instructor_id'],
      instructorName: json['instructor_name'] ?? '',
      instructorPhoto: json['instructor_photo'],
      scheduledDate: DateTime.parse(json['scheduled_date']),
      startTime: json['start_time'],
      endTime: json['end_time'],
      status: ClassStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => ClassStatus.scheduled,
      ),
      spotsBooked: json['spots_booked'] ?? 0,
      capacity: json['capacity'] ?? 20,
      isBooked: json['is_booked'] ?? false,
      isWaitlisted: json['is_waitlisted'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'class_id': classId,
      'class_info': classInfo?.toJson(),
      'instructor_id': instructorId,
      'instructor_name': instructorName,
      'instructor_photo': instructorPhoto,
      'scheduled_date': scheduledDate.toIso8601String(),
      'start_time': startTime,
      'end_time': endTime,
      'status': status.name,
      'spots_booked': spotsBooked,
      'capacity': capacity,
      'is_booked': isBooked,
      'is_waitlisted': isWaitlisted,
    };
  }

  bool get isFull => spotsBooked >= capacity;
  bool get hasSpots => spotsBooked < capacity;
  int get spotsRemaining => capacity - spotsBooked;
  double get fillPercentage => (spotsBooked / capacity * 100).clamp(0, 100);
}

enum ClassStatus {
  scheduled,
  ongoing,
  completed,
  cancelled,
}

class ClassBooking {
  final String id;
  final String scheduleId;
  final String memberId;
  final BookingStatus status;
  final DateTime bookedAt;
  final DateTime? cancelledAt;
  final DateTime? attendedAt;

  ClassBooking({
    required this.id,
    required this.scheduleId,
    required this.memberId,
    required this.status,
    required this.bookedAt,
    this.cancelledAt,
    this.attendedAt,
  });

  factory ClassBooking.fromJson(Map<String, dynamic> json) {
    return ClassBooking(
      id: json['id'],
      scheduleId: json['schedule_id'],
      memberId: json['member_id'],
      status: BookingStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => BookingStatus.booked,
      ),
      bookedAt: DateTime.parse(json['booked_at']),
      cancelledAt: json['cancelled_at'] != null
          ? DateTime.parse(json['cancelled_at'])
          : null,
      attendedAt: json['attended_at'] != null
          ? DateTime.parse(json['attended_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'schedule_id': scheduleId,
      'member_id': memberId,
      'status': status.name,
      'booked_at': bookedAt.toIso8601String(),
      'cancelled_at': cancelledAt?.toIso8601String(),
      'attended_at': attendedAt?.toIso8601String(),
    };
  }
}

enum BookingStatus {
  booked,
  attended,
  noShow,
  cancelled,
  waitlisted,
}
