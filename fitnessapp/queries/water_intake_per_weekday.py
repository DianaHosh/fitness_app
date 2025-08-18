from datetime import timedelta
from django.db.models import Sum, F, Value, DateField
from django.db.models.functions import Cast
from django.utils.timezone import now
from fitnessapp.models import WaterIntake

def get_water_intake_data(user_id=None):
    last_7_days = now() - timedelta(days=7)

    query = WaterIntake.objects.filter(
        intake_time__gte=last_7_days,
        **({'user_id': user_id} if user_id else {})
    ).exclude(
        intake_time__isnull=True
    ).annotate(
        day=Cast('intake_time', output_field=DateField())
    ).values(
        'day', 'user__username' if user_id else 'day'
    ).annotate(
        total_water_ml=Sum(F('glasses') * Value(250))
    ).order_by('day')

    return query
