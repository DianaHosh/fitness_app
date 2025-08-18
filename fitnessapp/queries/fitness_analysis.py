from django.db.models import Count, F
from fitnessapp.models import Workout

def get_workout_data():
    return Workout.objects.annotate(
        total_workouts=Count('workout_id'),
        workout_start_time=F('workout_time_begin'),
        workout_end_time=F('workout_time_end'),
        annotated_duration=F('duration'),
        username=F('user__username')
    ).filter(total_workouts__gt=0)

