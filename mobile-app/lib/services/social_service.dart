import 'package:dio/dio.dart';
import 'http_client.dart';

class SocialService {
  final HttpClient _httpClient = HttpClient();

  /// Get activity feed
  Future<List<Map<String, dynamic>>> getActivityFeed({
    int? limit,
    int? offset,
    String? filter, // 'all', 'friends', 'me'
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;
      if (filter != null) queryParams['filter'] = filter;

      final response = await _httpClient.get(
        '/social/feed',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get activity feed';
    }
  }

  /// Post activity/achievement
  Future<Map<String, dynamic>> postActivity({
    required String type, // 'workout', 'achievement', 'checkin', 'progress'
    required Map<String, dynamic> data,
    String? caption,
    List<String>? imageUrls,
  }) async {
    try {
      final response = await _httpClient.post(
        '/social/posts',
        data: {
          'type': type,
          'data': data,
          'caption': caption,
          'image_urls': imageUrls,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to post activity';
    }
  }

  /// Like post
  Future<void> likePost(String postId) async {
    try {
      await _httpClient.post('/social/posts/$postId/like');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to like post';
    }
  }

  /// Unlike post
  Future<void> unlikePost(String postId) async {
    try {
      await _httpClient.delete('/social/posts/$postId/like');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to unlike post';
    }
  }

  /// Comment on post
  Future<Map<String, dynamic>> commentOnPost({
    required String postId,
    required String comment,
  }) async {
    try {
      final response = await _httpClient.post(
        '/social/posts/$postId/comments',
        data: {'comment': comment},
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to comment';
    }
  }

  /// Get post comments
  Future<List<Map<String, dynamic>>> getComments(String postId) async {
    try {
      final response = await _httpClient.get(
        '/social/posts/$postId/comments',
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get comments';
    }
  }

  /// Delete post
  Future<void> deletePost(String postId) async {
    try {
      await _httpClient.delete('/social/posts/$postId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to delete post';
    }
  }

  /// Search members
  Future<List<Map<String, dynamic>>> searchMembers(String query) async {
    try {
      final response = await _httpClient.get(
        '/social/members/search',
        queryParameters: {'q': query},
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to search members';
    }
  }

  /// Get friends list
  Future<List<Map<String, dynamic>>> getFriends() async {
    try {
      final response = await _httpClient.get('/social/friends');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get friends';
    }
  }

  /// Send friend request
  Future<void> sendFriendRequest(String memberId) async {
    try {
      await _httpClient.post('/social/friends/request/$memberId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to send friend request';
    }
  }

  /// Accept friend request
  Future<void> acceptFriendRequest(String requestId) async {
    try {
      await _httpClient.post('/social/friends/accept/$requestId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to accept friend request';
    }
  }

  /// Reject friend request
  Future<void> rejectFriendRequest(String requestId) async {
    try {
      await _httpClient.delete('/social/friends/request/$requestId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to reject friend request';
    }
  }

  /// Remove friend
  Future<void> removeFriend(String memberId) async {
    try {
      await _httpClient.delete('/social/friends/$memberId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to remove friend';
    }
  }

  /// Get pending friend requests
  Future<List<Map<String, dynamic>>> getPendingRequests() async {
    try {
      final response = await _httpClient.get('/social/friends/pending');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get pending requests';
    }
  }

  /// Get leaderboards
  Future<Map<String, dynamic>> getLeaderboards({
    String? type, // 'visits', 'workouts', 'streak', 'weight_lifted'
    String? period, // 'week', 'month', 'all_time'
    String? filter, // 'all', 'friends'
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (type != null) queryParams['type'] = type;
      if (period != null) queryParams['period'] = period;
      if (filter != null) queryParams['filter'] = filter;

      final response = await _httpClient.get(
        '/social/leaderboards',
        queryParameters: queryParams,
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get leaderboards';
    }
  }

  /// Get challenges
  Future<List<Map<String, dynamic>>> getChallenges({
    String? status, // 'active', 'upcoming', 'completed'
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) queryParams['status'] = status;

      final response = await _httpClient.get(
        '/social/challenges',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get challenges';
    }
  }

  /// Join challenge
  Future<Map<String, dynamic>> joinChallenge(String challengeId) async {
    try {
      final response = await _httpClient.post(
        '/social/challenges/$challengeId/join',
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to join challenge';
    }
  }

  /// Leave challenge
  Future<void> leaveChallenge(String challengeId) async {
    try {
      await _httpClient.delete('/social/challenges/$challengeId/leave');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to leave challenge';
    }
  }

  /// Get challenge leaderboard
  Future<List<Map<String, dynamic>>> getChallengeLeaderboard(String challengeId) async {
    try {
      final response = await _httpClient.get(
        '/social/challenges/$challengeId/leaderboard',
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get challenge leaderboard';
    }
  }

  /// Get my challenges
  Future<List<Map<String, dynamic>>> getMyChallenges() async {
    try {
      final response = await _httpClient.get('/social/challenges/my');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get my challenges';
    }
  }

  /// Upload image for post
  Future<String> uploadImage(String filePath) async {
    try {
      final response = await _httpClient.uploadFile(
        '/social/upload-image',
        filePath,
      );

      return response.data['image_url'];
    } on DioException catch (e) {
      throw e.error ?? 'Failed to upload image';
    }
  }

  /// Report post
  Future<void> reportPost({
    required String postId,
    required String reason,
  }) async {
    try {
      await _httpClient.post(
        '/social/posts/$postId/report',
        data: {'reason': reason},
      );
    } on DioException catch (e) {
      throw e.error ?? 'Failed to report post';
    }
  }

  /// Block member
  Future<void> blockMember(String memberId) async {
    try {
      await _httpClient.post('/social/block/$memberId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to block member';
    }
  }

  /// Unblock member
  Future<void> unblockMember(String memberId) async {
    try {
      await _httpClient.delete('/social/block/$memberId');
    } on DioException catch (e) {
      throw e.error ?? 'Failed to unblock member';
    }
  }
}
