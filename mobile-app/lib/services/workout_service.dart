import 'package:dio/dio.dart';
import 'http_client.dart';
import 'storage_service.dart';

class WorkoutService {
  final HttpClient _httpClient = HttpClient();

  /// Get workout library
  Future<List<Map<String, dynamic>>> getWorkoutLibrary({
    String? goal,
    String? equipment,
    String? difficulty,
    int? duration,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (goal != null) queryParams['goal'] = goal;
      if (equipment != null) queryParams['equipment'] = equipment;
      if (difficulty != null) queryParams['difficulty'] = difficulty;
      if (duration != null) queryParams['duration'] = duration;

      final response = await _httpClient.get(
        '/workouts/library',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get workout library';
    }
  }

  /// Get workout by ID
  Future<Map<String, dynamic>> getWorkoutById(String workoutId) async {
    try {
      // Try to get from cache first (offline support)
      final cached = StorageService.getWorkout(workoutId);
      if (cached != null) {
        return cached;
      }

      // Fetch from server
      final response = await _httpClient.get('/workouts/$workoutId');
      final workout = response.data;

      // Cache for offline access
      await StorageService.saveWorkout(workoutId, workout);

      return workout;
    } on DioException catch (e) {
      // If offline, return cached version
      final cached = StorageService.getWorkout(workoutId);
      if (cached != null) {
        return cached;
      }

      throw e.error ?? 'Failed to get workout';
    }
  }

  /// Get exercise library
  Future<List<Map<String, dynamic>>> getExerciseLibrary({
    String? muscleGroup,
    String? equipment,
    String? difficulty,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (muscleGroup != null) queryParams['muscle_group'] = muscleGroup;
      if (equipment != null) queryParams['equipment'] = equipment;
      if (difficulty != null) queryParams['difficulty'] = difficulty;

      final response = await _httpClient.get(
        '/exercises',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get exercise library';
    }
  }

  /// Get exercise by ID
  Future<Map<String, dynamic>> getExerciseById(String exerciseId) async {
    try {
      final response = await _httpClient.get('/exercises/$exerciseId');
      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get exercise';
    }
  }

  /// Search exercises
  Future<List<Map<String, dynamic>>> searchExercises(String query) async {
    try {
      final response = await _httpClient.get(
        '/exercises/search',
        queryParameters: {'q': query},
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to search exercises';
    }
  }

  /// Create custom workout
  Future<Map<String, dynamic>> createWorkout({
    required String name,
    String? description,
    required List<Map<String, dynamic>> exercises,
    String? goal,
    String? difficulty,
  }) async {
    try {
      final response = await _httpClient.post(
        '/workouts',
        data: {
          'name': name,
          'description': description,
          'exercises': exercises,
          'goal': goal,
          'difficulty': difficulty,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to create workout';
    }
  }

  /// Update workout
  Future<Map<String, dynamic>> updateWorkout({
    required String workoutId,
    String? name,
    String? description,
    List<Map<String, dynamic>>? exercises,
    String? goal,
    String? difficulty,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (name != null) data['name'] = name;
      if (description != null) data['description'] = description;
      if (exercises != null) data['exercises'] = exercises;
      if (goal != null) data['goal'] = goal;
      if (difficulty != null) data['difficulty'] = difficulty;

      final response = await _httpClient.put(
        '/workouts/$workoutId',
        data: data,
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to update workout';
    }
  }

  /// Delete workout
  Future<void> deleteWorkout(String workoutId) async {
    try {
      await _httpClient.delete('/workouts/$workoutId');
      await StorageService.deleteWorkout(workoutId);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to delete workout';
    }
  }

  /// Log workout session
  Future<Map<String, dynamic>> logWorkout({
    required String workoutId,
    required DateTime startTime,
    required DateTime endTime,
    required List<Map<String, dynamic>> exerciseLogs,
    String? notes,
    int? caloriesBurned,
  }) async {
    try {
      final workoutLog = {
        'workout_id': workoutId,
        'start_time': startTime.toIso8601String(),
        'end_time': endTime.toIso8601String(),
        'exercise_logs': exerciseLogs,
        'notes': notes,
        'calories_burned': caloriesBurned,
      };

      final response = await _httpClient.post(
        '/workouts/logs',
        data: workoutLog,
      );

      return response.data;
    } on DioException catch (e) {
      // If offline, save to pending logs
      if (e.type == DioExceptionType.unknown ||
          e.type == DioExceptionType.connectionTimeout) {
        await StorageService.savePendingWorkoutLog({
          'workout_id': workoutId,
          'start_time': startTime.toIso8601String(),
          'end_time': endTime.toIso8601String(),
          'exercise_logs': exerciseLogs,
          'notes': notes,
          'calories_burned': caloriesBurned,
        });

        return {
          'status': 'offline',
          'message': 'Workout saved locally and will sync when online',
        };
      }

      throw e.error ?? 'Failed to log workout';
    }
  }

  /// Get workout history
  Future<List<Map<String, dynamic>>> getWorkoutHistory({
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }
      if (limit != null) queryParams['limit'] = limit;

      final response = await _httpClient.get(
        '/workouts/logs',
        queryParameters: queryParams,
      );

      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get workout history';
    }
  }

  /// Get workout stats
  Future<Map<String, dynamic>> getWorkoutStats({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }

      final response = await _httpClient.get(
        '/workouts/stats',
        queryParameters: queryParams,
      );

      return response.data;
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get workout stats';
    }
  }

  /// Get personal records
  Future<List<Map<String, dynamic>>> getPersonalRecords() async {
    try {
      final response = await _httpClient.get('/workouts/personal-records');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get personal records';
    }
  }

  /// Sync pending workout logs (when coming back online)
  Future<void> syncPendingLogs() async {
    try {
      final pendingLogs = StorageService.getPendingWorkoutLogs();

      if (pendingLogs.isEmpty) return;

      // Sync each log
      for (var log in pendingLogs) {
        try {
          await _httpClient.post('/workouts/logs', data: log);
        } catch (e) {
          print('Failed to sync workout log: $e');
        }
      }

      // Clear pending logs after successful sync
      await StorageService.clearPendingWorkoutLogs();
    } catch (e) {
      print('Failed to sync pending logs: $e');
    }
  }

  /// Get my workouts (created by user)
  Future<List<Map<String, dynamic>>> getMyWorkouts() async {
    try {
      final response = await _httpClient.get('/workouts/my-workouts');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get workouts';
    }
  }

  /// Get recommended workouts (AI-powered)
  Future<List<Map<String, dynamic>>> getRecommendedWorkouts() async {
    try {
      final response = await _httpClient.get('/workouts/recommended');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get recommendations';
    }
  }

  /// Get workout categories
  Future<List<String>> getCategories() async {
    try {
      final response = await _httpClient.get('/workouts/categories');
      return List<String>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get categories';
    }
  }

  /// Get muscle groups
  Future<List<String>> getMuscleGroups() async {
    try {
      final response = await _httpClient.get('/exercises/muscle-groups');
      return List<String>.from(response.data);
    } on DioException catch (e) {
      throw e.error ?? 'Failed to get muscle groups';
    }
  }
}
