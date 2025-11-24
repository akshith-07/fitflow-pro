class Workout {
  final String id;
  final String name;
  final String? description;
  final String memberId;
  final DateTime startTime;
  final DateTime? endTime;
  final int? durationMinutes;
  final List<Exercise> exercises;
  final String? notes;
  final List<String>? photos;
  final WorkoutType type;

  Workout({
    required this.id,
    required this.name,
    this.description,
    required this.memberId,
    required this.startTime,
    this.endTime,
    this.durationMinutes,
    required this.exercises,
    this.notes,
    this.photos,
    required this.type,
  });

  factory Workout.fromJson(Map<String, dynamic> json) {
    return Workout(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      memberId: json['member_id'],
      startTime: DateTime.parse(json['start_time']),
      endTime:
          json['end_time'] != null ? DateTime.parse(json['end_time']) : null,
      durationMinutes: json['duration_minutes'],
      exercises: (json['exercises'] as List?)
              ?.map((e) => Exercise.fromJson(e))
              .toList() ??
          [],
      notes: json['notes'],
      photos: json['photos'] != null ? List<String>.from(json['photos']) : null,
      type: WorkoutType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => WorkoutType.strength,
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'member_id': memberId,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime?.toIso8601String(),
      'duration_minutes': durationMinutes,
      'exercises': exercises.map((e) => e.toJson()).toList(),
      'notes': notes,
      'photos': photos,
      'type': type.name,
    };
  }

  int get totalSets => exercises.fold(0, (sum, e) => sum + e.sets.length);
  double get totalVolume =>
      exercises.fold(0.0, (sum, e) => sum + e.totalVolume);
}

enum WorkoutType {
  strength,
  cardio,
  flexibility,
  sports,
  other,
}

class Exercise {
  final String id;
  final String name;
  final String? muscleGroup;
  final String? equipment;
  final String? instructions;
  final String? videoUrl;
  final String? thumbnailUrl;
  final List<ExerciseSet> sets;
  final int? restSeconds;

  Exercise({
    required this.id,
    required this.name,
    this.muscleGroup,
    this.equipment,
    this.instructions,
    this.videoUrl,
    this.thumbnailUrl,
    required this.sets,
    this.restSeconds,
  });

  factory Exercise.fromJson(Map<String, dynamic> json) {
    return Exercise(
      id: json['id'],
      name: json['name'],
      muscleGroup: json['muscle_group'],
      equipment: json['equipment'],
      instructions: json['instructions'],
      videoUrl: json['video_url'],
      thumbnailUrl: json['thumbnail_url'],
      sets: (json['sets'] as List?)
              ?.map((e) => ExerciseSet.fromJson(e))
              .toList() ??
          [],
      restSeconds: json['rest_seconds'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'muscle_group': muscleGroup,
      'equipment': equipment,
      'instructions': instructions,
      'video_url': videoUrl,
      'thumbnail_url': thumbnailUrl,
      'sets': sets.map((e) => e.toJson()).toList(),
      'rest_seconds': restSeconds,
    };
  }

  double get totalVolume {
    return sets.fold(0.0, (sum, set) {
      if (set.weight != null && set.reps != null) {
        return sum + (set.weight! * set.reps!);
      }
      return sum;
    });
  }
}

class ExerciseSet {
  final int setNumber;
  final int? reps;
  final double? weight;
  final int? durationSeconds;
  final double? distance;
  final bool completed;
  final String? notes;

  ExerciseSet({
    required this.setNumber,
    this.reps,
    this.weight,
    this.durationSeconds,
    this.distance,
    this.completed = false,
    this.notes,
  });

  factory ExerciseSet.fromJson(Map<String, dynamic> json) {
    return ExerciseSet(
      setNumber: json['set_number'],
      reps: json['reps'],
      weight: json['weight']?.toDouble(),
      durationSeconds: json['duration_seconds'],
      distance: json['distance']?.toDouble(),
      completed: json['completed'] ?? false,
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'set_number': setNumber,
      'reps': reps,
      'weight': weight,
      'duration_seconds': durationSeconds,
      'distance': distance,
      'completed': completed,
      'notes': notes,
    };
  }
}

class WorkoutPlan {
  final String id;
  final String name;
  final String? description;
  final String? createdBy;
  final int durationWeeks;
  final List<WorkoutDay> days;
  final DifficultyLevel difficulty;
  final List<String> goals;

  WorkoutPlan({
    required this.id,
    required this.name,
    this.description,
    this.createdBy,
    required this.durationWeeks,
    required this.days,
    required this.difficulty,
    required this.goals,
  });

  factory WorkoutPlan.fromJson(Map<String, dynamic> json) {
    return WorkoutPlan(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      createdBy: json['created_by'],
      durationWeeks: json['duration_weeks'] ?? 4,
      days: (json['days'] as List?)
              ?.map((e) => WorkoutDay.fromJson(e))
              .toList() ??
          [],
      difficulty: DifficultyLevel.values.firstWhere(
        (e) => e.name == json['difficulty'],
        orElse: () => DifficultyLevel.beginner,
      ),
      goals: List<String>.from(json['goals'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'created_by': createdBy,
      'duration_weeks': durationWeeks,
      'days': days.map((e) => e.toJson()).toList(),
      'difficulty': difficulty.name,
      'goals': goals,
    };
  }
}

class WorkoutDay {
  final int dayNumber;
  final String name;
  final List<Exercise> exercises;

  WorkoutDay({
    required this.dayNumber,
    required this.name,
    required this.exercises,
  });

  factory WorkoutDay.fromJson(Map<String, dynamic> json) {
    return WorkoutDay(
      dayNumber: json['day_number'],
      name: json['name'],
      exercises: (json['exercises'] as List?)
              ?.map((e) => Exercise.fromJson(e))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'day_number': dayNumber,
      'name': name,
      'exercises': exercises.map((e) => e.toJson()).toList(),
    };
  }
}
