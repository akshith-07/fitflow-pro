import 'dart:convert';

class User {
  final String id;
  final String organizationId;
  final String email;
  final String firstName;
  final String lastName;
  final String? phone;
  final String role;
  final String? profilePhotoUrl;
  final bool isActive;
  final bool isVerified;
  final DateTime? lastLoginAt;
  final DateTime createdAt;
  final DateTime updatedAt;

  User({
    required this.id,
    required this.organizationId,
    required this.email,
    required this.firstName,
    required this.lastName,
    this.phone,
    required this.role,
    this.profilePhotoUrl,
    required this.isActive,
    required this.isVerified,
    this.lastLoginAt,
    required this.createdAt,
    required this.updatedAt,
  });

  String get fullName => '$firstName $lastName';

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      organizationId: json['organization_id'],
      email: json['email'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      phone: json['phone'],
      role: json['role'],
      profilePhotoUrl: json['profile_photo_url'],
      isActive: json['is_active'],
      isVerified: json['is_verified'],
      lastLoginAt: json['last_login_at'] != null
          ? DateTime.parse(json['last_login_at'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'organization_id': organizationId,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'phone': phone,
      'role': role,
      'profile_photo_url': profilePhotoUrl,
      'is_active': isActive,
      'is_verified': isVerified,
      'last_login_at': lastLoginAt?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  String toJsonString() => json.encode(toJson());

  factory User.fromJsonString(String jsonString) {
    return User.fromJson(json.decode(jsonString));
  }

  User copyWith({
    String? id,
    String? organizationId,
    String? email,
    String? firstName,
    String? lastName,
    String? phone,
    String? role,
    String? profilePhotoUrl,
    bool? isActive,
    bool? isVerified,
    DateTime? lastLoginAt,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      organizationId: organizationId ?? this.organizationId,
      email: email ?? this.email,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      phone: phone ?? this.phone,
      role: role ?? this.role,
      profilePhotoUrl: profilePhotoUrl ?? this.profilePhotoUrl,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
