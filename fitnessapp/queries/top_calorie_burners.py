from fitnessapp.models import Workout
from django.db.models import Sum
from django.db.models.functions import Cast
from django.db.models import DateField

def get_daily_calories_data(start_date, end_date, user_id=None):
    query = Workout.objects.filter(
        workout_time_begin__gte=start_date,
        workout_time_end__lte=end_date
    )

    if user_id:
        query = query.filter(user_id=user_id)

    data = (
        query
        .annotate(day=Cast('workout_time_begin', output_field=DateField()))
        .values('day', 'user__username')
        .annotate(total_calories_burned=Sum('burned_calories'))
        .order_by('day', 'user__username')
    )
    return list(data)
