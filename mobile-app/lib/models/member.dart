import 'dart:convert';

class Member {
  final String id;
  final String organizationId;
  final String userId;
  final String memberId;
  final DateTime? dateOfBirth;
  final String? gender;
  final Map<String, dynamic>? address;
  final String? emergencyContactName;
  final String? emergencyContactPhone;
  final String? medicalNotes;
  final Map<String, dynamic>? fitnessGoals;
  final List<String>? tags;
  final String? profilePhotoUrl;
  final String? qrCode;
  final String status;
  final DateTime joinedAt;
  final DateTime createdAt;
  final DateTime updatedAt;

  Member({
    required this.id,
    required this.organizationId,
    required this.userId,
    required this.memberId,
    this.dateOfBirth,
    this.gender,
    this.address,
    this.emergencyContactName,
    this.emergencyContactPhone,
    this.medicalNotes,
    this.fitnessGoals,
    this.tags,
    this.profilePhotoUrl,
    this.qrCode,
    required this.status,
    required this.joinedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Member.fromJson(Map<String, dynamic> json) {
    return Member(
      id: json['id'],
      organizationId: json['organization_id'],
      userId: json['user_id'],
      memberId: json['member_id'],
      dateOfBirth: json['date_of_birth'] != null
          ? DateTime.parse(json['date_of_birth'])
          : null,
      gender: json['gender'],
      address: json['address'],
      emergencyContactName: json['emergency_contact_name'],
      emergencyContactPhone: json['emergency_contact_phone'],
      medicalNotes: json['medical_notes'],
      fitnessGoals: json['fitness_goals'],
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
      profilePhotoUrl: json['profile_photo_url'],
      qrCode: json['qr_code'],
      status: json['status'],
      joinedAt: DateTime.parse(json['joined_at']),
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'organization_id': organizationId,
      'user_id': userId,
      'member_id': memberId,
      'date_of_birth': dateOfBirth?.toIso8601String(),
      'gender': gender,
      'address': address,
      'emergency_contact_name': emergencyContactName,
      'emergency_contact_phone': emergencyContactPhone,
      'medical_notes': medicalNotes,
      'fitness_goals': fitnessGoals,
      'tags': tags,
      'profile_photo_url': profilePhotoUrl,
      'qr_code': qrCode,
      'status': status,
      'joined_at': joinedAt.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  String toJsonString() => json.encode(toJson());

  factory Member.fromJsonString(String jsonString) {
    return Member.fromJson(json.decode(jsonString));
  }

  Member copyWith({
    String? id,
    String? organizationId,
    String? userId,
    String? memberId,
    DateTime? dateOfBirth,
    String? gender,
    Map<String, dynamic>? address,
    String? emergencyContactName,
    String? emergencyContactPhone,
    String? medicalNotes,
    Map<String, dynamic>? fitnessGoals,
    List<String>? tags,
    String? profilePhotoUrl,
    String? qrCode,
    String? status,
    DateTime? joinedAt,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Member(
      id: id ?? this.id,
      organizationId: organizationId ?? this.organizationId,
      userId: userId ?? this.userId,
      memberId: memberId ?? this.memberId,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      gender: gender ?? this.gender,
      address: address ?? this.address,
      emergencyContactName: emergencyContactName ?? this.emergencyContactName,
      emergencyContactPhone:
          emergencyContactPhone ?? this.emergencyContactPhone,
      medicalNotes: medicalNotes ?? this.medicalNotes,
      fitnessGoals: fitnessGoals ?? this.fitnessGoals,
      tags: tags ?? this.tags,
      profilePhotoUrl: profilePhotoUrl ?? this.profilePhotoUrl,
      qrCode: qrCode ?? this.qrCode,
      status: status ?? this.status,
      joinedAt: joinedAt ?? this.joinedAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
