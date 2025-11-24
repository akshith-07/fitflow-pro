import 'package:flutter/foundation.dart';
import '../models/workout.dart';
import '../services/http_client.dart';

class WorkoutProvider with ChangeNotifier {
  List<Workout> _workouts = [];
  List<WorkoutPlan> _plans = [];
  Workout? _activeWorkout;
  bool _isLoading = false;
  String? _error;

  List<Workout> get workouts => _workouts;
  List<WorkoutPlan> get plans => _plans;
  Workout? get activeWorkout => _activeWorkout;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasActiveWorkout => _activeWorkout != null;

  final ApiClient _apiClient = ApiClient();

  Future<void> fetchWorkouts() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiClient.get('/workouts');
      if (response != null && response is List) {
        _workouts = response.map((json) => Workout.fromJson(json)).toList();
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchWorkoutPlans() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiClient.get('/workout-plans');
      if (response != null && response is List) {
        _plans = response.map((json) => WorkoutPlan.fromJson(json)).toList();
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  void startWorkout(Workout workout) {
    _activeWorkout = workout;
    notifyListeners();
  }

  void updateActiveWorkout(Workout workout) {
    _activeWorkout = workout;
    notifyListeners();
  }

  Future<bool> saveWorkout(Workout workout) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response =
          await _apiClient.post('/workouts', workout.toJson());
      if (response != null) {
        final savedWorkout = Workout.fromJson(response);
        _workouts.insert(0, savedWorkout);
        _activeWorkout = null;
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  void cancelWorkout() {
    _activeWorkout = null;
    notifyListeners();
  }
}
