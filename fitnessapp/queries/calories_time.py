from fitnessapp.models import Workout

def get_workout_data(start_date, end_date, user_id=None):
    query = Workout.objects.filter(
        workout_time_begin__gte=start_date,
        workout_time_end__lte=end_date
    )
    if user_id:
        query = query.filter(user_id=user_id)

    data = (
        query
        .values('workout_time_begin', 'user__username', 'duration', 'burned_calories')
        .order_by('workout_time_begin')
    )

    return data
