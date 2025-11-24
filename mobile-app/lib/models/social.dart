class SocialPost {
  final String id;
  final String memberId;
  final String memberName;
  final String? memberPhoto;
  final String? content;
  final PostType type;
  final Map<String, dynamic>? data;
  final List<String>? photos;
  final DateTime createdAt;
  final int likesCount;
  final int commentsCount;
  final bool isLiked;

  SocialPost({
    required this.id,
    required this.memberId,
    required this.memberName,
    this.memberPhoto,
    this.content,
    required this.type,
    this.data,
    this.photos,
    required this.createdAt,
    required this.likesCount,
    required this.commentsCount,
    this.isLiked = false,
  });

  factory SocialPost.fromJson(Map<String, dynamic> json) {
    return SocialPost(
      id: json['id'],
      memberId: json['member_id'],
      memberName: json['member_name'],
      memberPhoto: json['member_photo'],
      content: json['content'],
      type: PostType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => PostType.general,
      ),
      data: json['data'],
      photos: json['photos'] != null ? List<String>.from(json['photos']) : null,
      createdAt: DateTime.parse(json['created_at']),
      likesCount: json['likes_count'] ?? 0,
      commentsCount: json['comments_count'] ?? 0,
      isLiked: json['is_liked'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'member_id': memberId,
      'member_name': memberName,
      'member_photo': memberPhoto,
      'content': content,
      'type': type.name,
      'data': data,
      'photos': photos,
      'created_at': createdAt.toIso8601String(),
      'likes_count': likesCount,
      'comments_count': commentsCount,
      'is_liked': isLiked,
    };
  }
}

enum PostType {
  workout,
  progress,
  achievement,
  checkIn,
  general,
}

class Comment {
  final String id;
  final String postId;
  final String memberId;
  final String memberName;
  final String? memberPhoto;
  final String content;
  final DateTime createdAt;

  Comment({
    required this.id,
    required this.postId,
    required this.memberId,
    required this.memberName,
    this.memberPhoto,
    required this.content,
    required this.createdAt,
  });

  factory Comment.fromJson(Map<String, dynamic> json) {
    return Comment(
      id: json['id'],
      postId: json['post_id'],
      memberId: json['member_id'],
      memberName: json['member_name'],
      memberPhoto: json['member_photo'],
      content: json['content'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'post_id': postId,
      'member_id': memberId,
      'member_name': memberName,
      'member_photo': memberPhoto,
      'content': content,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class Challenge {
  final String id;
  final String title;
  final String description;
  final DateTime startDate;
  final DateTime endDate;
  final ChallengeType type;
  final Map<String, dynamic> rules;
  final String? imageUrl;
  final int participantsCount;
  final bool isParticipating;
  final List<ChallengeLeaderboard>? leaderboard;

  Challenge({
    required this.id,
    required this.title,
    required this.description,
    required this.startDate,
    required this.endDate,
    required this.type,
    required this.rules,
    this.imageUrl,
    required this.participantsCount,
    this.isParticipating = false,
    this.leaderboard,
  });

  factory Challenge.fromJson(Map<String, dynamic> json) {
    return Challenge(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      type: ChallengeType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => ChallengeType.steps,
      ),
      rules: json['rules'] ?? {},
      imageUrl: json['image_url'],
      participantsCount: json['participants_count'] ?? 0,
      isParticipating: json['is_participating'] ?? false,
      leaderboard: json['leaderboard'] != null
          ? (json['leaderboard'] as List)
              .map((e) => ChallengeLeaderboard.fromJson(e))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
      'type': type.name,
      'rules': rules,
      'image_url': imageUrl,
      'participants_count': participantsCount,
      'is_participating': isParticipating,
      'leaderboard': leaderboard?.map((e) => e.toJson()).toList(),
    };
  }

  bool get isActive {
    final now = DateTime.now();
    return now.isAfter(startDate) && now.isBefore(endDate);
  }

  bool get isUpcoming => DateTime.now().isBefore(startDate);
  bool get isCompleted => DateTime.now().isAfter(endDate);
}

enum ChallengeType {
  steps,
  workouts,
  weightLoss,
  strength,
  attendance,
  custom,
}

class ChallengeLeaderboard {
  final int rank;
  final String memberId;
  final String memberName;
  final String? memberPhoto;
  final double score;
  final Map<String, dynamic>? details;

  ChallengeLeaderboard({
    required this.rank,
    required this.memberId,
    required this.memberName,
    this.memberPhoto,
    required this.score,
    this.details,
  });

  factory ChallengeLeaderboard.fromJson(Map<String, dynamic> json) {
    return ChallengeLeaderboard(
      rank: json['rank'],
      memberId: json['member_id'],
      memberName: json['member_name'],
      memberPhoto: json['member_photo'],
      score: (json['score'] ?? 0).toDouble(),
      details: json['details'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'rank': rank,
      'member_id': memberId,
      'member_name': memberName,
      'member_photo': memberPhoto,
      'score': score,
      'details': details,
    };
  }
}

class Friend {
  final String id;
  final String memberId;
  final String memberName;
  final String? memberPhoto;
  final FriendshipStatus status;
  final DateTime createdAt;

  Friend({
    required this.id,
    required this.memberId,
    required this.memberName,
    this.memberPhoto,
    required this.status,
    required this.createdAt,
  });

  factory Friend.fromJson(Map<String, dynamic> json) {
    return Friend(
      id: json['id'],
      memberId: json['member_id'],
      memberName: json['member_name'],
      memberPhoto: json['member_photo'],
      status: FriendshipStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => FriendshipStatus.pending,
      ),
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'member_id': memberId,
      'member_name': memberName,
      'member_photo': memberPhoto,
      'status': status.name,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

enum FriendshipStatus {
  pending,
  accepted,
  blocked,
}
